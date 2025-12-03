from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction as db_transaction
from django.utils import timezone

from .models import PlatformWallet, WalletTransaction


class InsufficientBalanceError(Exception):
    """Raised when a wallet debit would result in a negative balance."""


@dataclass(frozen=True)
class TransactionResult:
    transaction: WalletTransaction
    balance_before: int
    balance_after: int


def create_pending_transaction(*, user, amount: int, direction: str, category: str, note: str = "", job=None, initiated_by=None) -> WalletTransaction:
    return WalletTransaction.objects.create(
        user=user,
        initiated_by=initiated_by,
        job=job,
        direction=direction,
        category=category,
        amount=amount,
        note=note,
    )


def apply_wallet_transaction(*, user, amount: int, direction: str, category: str, note: str = "", job=None, initiated_by=None) -> TransactionResult:
    from userprofile.models import UserProfile

    with db_transaction.atomic():
        profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)
        balance_before = profile.wallet_balance
        balance_after = _calculate_balance(balance_before, amount, direction)
        platform_balance_before, platform_balance_after = _update_platform_balance(amount, direction)
        profile.wallet_balance = balance_after
        profile.save(update_fields=["wallet_balance"])
        txn = WalletTransaction.objects.create(
            user=user,
            initiated_by=initiated_by,
            job=job,
            direction=direction,
            category=category,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            platform_balance_before=platform_balance_before,
            platform_balance_after=platform_balance_after,
            status=WalletTransaction.Status.COMPLETED,
            processed_at=timezone.now(),
            note=note,
        )
    return TransactionResult(transaction=txn, balance_before=balance_before, balance_after=balance_after)


def mark_transaction_completed(transaction: WalletTransaction, acting_user=None) -> TransactionResult:
    if transaction.status == WalletTransaction.Status.COMPLETED:
        return TransactionResult(
            transaction=transaction,
            balance_before=transaction.balance_before or 0,
            balance_after=transaction.balance_after or 0,
        )
    from userprofile.models import UserProfile

    with db_transaction.atomic():
        profile, _ = UserProfile.objects.select_for_update().get_or_create(user=transaction.user)
        balance_before = profile.wallet_balance
        balance_after = _calculate_balance(balance_before, transaction.amount, transaction.direction)
        platform_balance_before, platform_balance_after = _update_platform_balance(transaction.amount, transaction.direction)
        profile.wallet_balance = balance_after
        profile.save(update_fields=["wallet_balance"])
        transaction.balance_before = balance_before
        transaction.balance_after = balance_after
        transaction.platform_balance_before = platform_balance_before
        transaction.platform_balance_after = platform_balance_after
        transaction.status = WalletTransaction.Status.COMPLETED
        transaction.processed_at = timezone.now()
        if acting_user and not transaction.initiated_by:
            transaction.initiated_by = acting_user
        transaction.save(update_fields=[
            "balance_before",
            "balance_after",
            "platform_balance_before",
            "platform_balance_after",
            "status",
            "processed_at",
            "initiated_by",
        ])
    return TransactionResult(transaction=transaction, balance_before=balance_before, balance_after=balance_after)


def _calculate_balance(balance_before: int, amount: int, direction: str) -> int:
    if direction == WalletTransaction.Direction.USER_TO_JOBFLICK:
        if balance_before < amount:
            raise InsufficientBalanceError("Insufficient wallet balance for this payment.")
        return balance_before - amount
    return balance_before + amount


def _update_platform_balance(amount: int, direction: str) -> tuple[int, int]:
    wallet = PlatformWallet.load(for_update=True)
    balance_before = wallet.balance
    if direction == WalletTransaction.Direction.USER_TO_JOBFLICK:
        wallet.balance = balance_before + amount
    else:
        if wallet.balance < amount:
            raise InsufficientBalanceError("Jobflick does not have enough balance for this payout.")
        wallet.balance = balance_before - amount
    wallet.save(update_fields=["balance", "updated_at"])
    return balance_before, wallet.balance
