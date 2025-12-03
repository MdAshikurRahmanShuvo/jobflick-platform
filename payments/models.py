from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string


class WalletTransaction(models.Model):
    class Direction(models.TextChoices):
        USER_TO_JOBFLICK = "user_to_jobflick", "User -> Jobflick"
        JOBFLICK_TO_USER = "jobflick_to_user", "Jobflick -> User"

    class Category(models.TextChoices):
        SUBSCRIPTION = "subscription", "Subscription"
        SERVICE_FEE = "service_fee", "Service Fee"
        TOP_UP = "top_up", "Wallet Top-up"
        PAYOUT = "payout", "Payout"
        REFUND = "refund", "Refund"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    reference = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet_transactions",
    )
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiated_wallet_transactions",
    )
    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wallet_transactions",
    )
    direction = models.CharField(max_length=32, choices=Direction.choices)
    category = models.CharField(max_length=32, choices=Category.choices, default=Category.OTHER)
    amount = models.PositiveIntegerField()
    balance_before = models.PositiveIntegerField(null=True, blank=True)
    balance_after = models.PositiveIntegerField(null=True, blank=True)
    platform_balance_before = models.PositiveIntegerField(null=True, blank=True)
    platform_balance_after = models.PositiveIntegerField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.reference} ({self.user})"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_reference() -> str:
        return f"TX-{get_random_string(8).upper()}"

    @property
    def is_credit(self) -> bool:
        return self.direction == self.Direction.JOBFLICK_TO_USER

    @property
    def is_debit(self) -> bool:
        return self.direction == self.Direction.USER_TO_JOBFLICK

    def mark_processing(self, actor=None):
        if self.status == self.Status.PENDING:
            self.status = self.Status.PROCESSING
            if actor and not self.initiated_by:
                self.initiated_by = actor
            self.save(update_fields=["status", "initiated_by"])

    def mark_failed(self, reason: str = ""):
        self.status = self.Status.FAILED
        if reason:
            self.note = reason
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "note", "processed_at"])


class PlatformWallet(models.Model):
    balance = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Jobflick wallet"
        verbose_name_plural = "Jobflick wallet"

    def __str__(self) -> str:
        return f"Jobflick balance: {self.balance} BDT"

    @classmethod
    def load(cls, *, for_update: bool = False) -> "PlatformWallet":
        queryset = cls.objects
        if for_update:
            queryset = queryset.select_for_update()
        wallet, _ = queryset.get_or_create(pk=1, defaults={"balance": 0})
        return wallet

    @classmethod
    def current_balance(cls) -> int:
        wallet = cls.objects.order_by("pk").first()
        return wallet.balance if wallet else 0
