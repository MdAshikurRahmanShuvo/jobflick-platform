from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from jobs.models import Job, JobApplication

from .forms import AdminLoginForm, TransactionForm
from .models import Transaction


SECTION_COPY = {
	"users": {"title": "Users", "subtitle": "See all registered members."},
	"jobs": {"title": "Jobs", "subtitle": "Review every job post."},
	"approvals": {"title": "Job Approve", "subtitle": "Decide who gets approved."},
	"transactions": {"title": "Transactions", "subtitle": "Track platform funds."},
}


def _redirect_to_section(section: str):
	section = section if section in SECTION_COPY else "users"
	return redirect(f"{reverse('adminpanel-dashboard')}?section={section}")


def staff_required(view_func):
	@wraps(view_func)
	def _wrapped(request, *args, **kwargs):
		if not request.user.is_authenticated:
			return redirect("adminpanel-login")
		if not request.user.is_staff:
			messages.error(request, "You do not have permission to access the admin panel.")
			return redirect("adminpanel-login")
		return view_func(request, *args, **kwargs)

	return _wrapped


def login_view(request):
	if request.user.is_authenticated and request.user.is_staff:
		return redirect("adminpanel-dashboard")
	form = AdminLoginForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		user = form.cleaned_data["user"]
		login(request, user)
		messages.success(request, "Welcome back to the admin panel.")
		return redirect("adminpanel-dashboard")
	return render(request, "adminpanel/login.html", {"form": form, "hide_nav": True, "hide_footer": True})


@staff_required
def logout_view(request):
	logout(request)
	messages.info(request, "You have been logged out.")
	return redirect("adminpanel-login")


@staff_required
def dashboard_view(request):
	section = request.GET.get("section", "users").lower()
	if section not in SECTION_COPY:
		section = "users"
	context = {
		"section": section,
		"section_title": SECTION_COPY[section]["title"],
		"section_subtitle": SECTION_COPY[section]["subtitle"],
		"hide_nav": True,
		"hide_footer": True,
	}
	if section == "users":
		context["users"] = User.objects.order_by("-date_joined")
	elif section == "jobs":
		context["jobs"] = Job.objects.select_related("poster").order_by("-created_at")
	elif section == "approvals":
		context["applications"] = (
			JobApplication.objects.select_related("job", "applicant", "decided_by")
			.order_by("-created_at")
		)
	elif section == "transactions":
		transactions = Transaction.objects.select_related("recipient", "job").order_by("-created_at")
		aggregates = transactions.aggregate(total_amount=Sum("amount"))
		context.update(
			{
				"transactions": transactions,
				"total_amount": aggregates.get("total_amount") or 0,
			}
		)
	return render(request, "adminpanel/dashboard.html", context)


@staff_required
@require_POST
def delete_user(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	if user == request.user:
		messages.error(request, "You cannot delete your own account.")
	else:
		user.delete()
		messages.success(request, "User deleted successfully.")
	return _redirect_to_section("users")


@staff_required
@require_POST
def delete_job(request, job_id):
	job = get_object_or_404(Job, pk=job_id)
	job.delete()
	messages.success(request, "Job removed successfully.")
	return _redirect_to_section("jobs")


@staff_required
@require_POST
def handle_application_status(request, pk):
	application = get_object_or_404(JobApplication, pk=pk)
	action = request.POST.get("action")
	if action not in {"approve", "decline"}:
		messages.error(request, "Invalid action.")
		return redirect("adminpanel-dashboard")
	application.status = (
		JobApplication.Status.APPROVED if action == "approve" else JobApplication.Status.REJECTED
	)
	application.decided_by = request.user
	application.decision_at = timezone.now()
	application.save()
	messages.success(request, f"Application marked as {application.get_status_display().lower()}.")
	return _redirect_to_section("approvals")


@staff_required
@require_POST
def create_transaction(request):
	form = TransactionForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, "Transaction recorded successfully.")
	else:
		messages.error(request, "Please fix the errors in the transaction form.")
	return _redirect_to_section("transactions")


@staff_required
@require_POST
def mark_transaction_paid(request, pk):
	transaction = get_object_or_404(Transaction, pk=pk)
	transaction.status = Transaction.Status.PAID
	transaction.processed_at = timezone.now()
	transaction.save(update_fields=["status", "processed_at"])
	messages.success(request, "Transaction marked as paid.")
	return _redirect_to_section("transactions")
