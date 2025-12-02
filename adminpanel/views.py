from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from jobs.models import Job, JobApplication
from userprofile.models import Notification, UserProfile

from .forms import AdminLoginForm, TransactionForm
from .models import SubscriptionLedgerEntry, Transaction


ADMIN_SESSION_KEY = "adminpanel_user_id"
User = get_user_model()


def _get_admin_user(request):
	if hasattr(request, "_admin_user_cache"):
		return request._admin_user_cache
	user_id = request.session.get(ADMIN_SESSION_KEY)
	if not user_id:
		request._admin_user_cache = None
		return None
	try:
		user = User.objects.get(pk=user_id, is_staff=True)
	except User.DoesNotExist:
		request.session.pop(ADMIN_SESSION_KEY, None)
		user = None
	request._admin_user_cache = user
	return user


def _set_admin_session(request, user):
	request.session[ADMIN_SESSION_KEY] = user.pk
	request._admin_user_cache = user
	request.session.modified = True


def _clear_admin_session(request):
	request.session.pop(ADMIN_SESSION_KEY, None)
	request._admin_user_cache = None
	request.session.modified = True


SECTION_COPY = {
	"users": {"title": "Users", "subtitle": "See all registered members."},
	"jobs": {"title": "Jobs", "subtitle": "Review every job post."},
	"post-approvals": {"title": "Post Approvals", "subtitle": "Approve or remove newly submitted jobs."},
	"approvals": {"title": "Job Approve", "subtitle": "Decide who gets approved."},
	"transactions": {"title": "Transactions", "subtitle": "Track platform funds."},
	"subscribers": {"title": "Subscribers", "subtitle": "See who activated paid plans."},
	"notifications": {"title": "Notifications", "subtitle": "Stay on top of user activity."},
}


def _redirect_to_section(section: str):
	section = section if section in SECTION_COPY else "users"
	return redirect(f"{reverse('adminpanel-dashboard')}?section={section}")


def staff_required(view_func):
	@wraps(view_func)
	def _wrapped(request, *args, **kwargs):
		admin_user = _get_admin_user(request)
		if not admin_user:
			messages.error(request, "Please sign in to the admin panel.")
			return redirect("adminpanel-login")
		request.admin_user = admin_user
		return view_func(request, *args, **kwargs)

	return _wrapped


def login_view(request):
	if _get_admin_user(request):
		return redirect("adminpanel-dashboard")
	form = AdminLoginForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		user = form.cleaned_data["user"]
		_set_admin_session(request, user)
		messages.success(request, "Welcome back to the admin panel.")
		return redirect("adminpanel-dashboard")
	return render(request, "adminpanel/login.html", {"form": form, "hide_nav": True, "hide_footer": True})


@staff_required
def logout_view(request):
	_clear_admin_session(request)
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
		"admin_user": request.admin_user,
	}
	if section == "users":
		context["users"] = User.objects.order_by("-date_joined")
	elif section == "jobs":
		context["jobs"] = Job.objects.select_related("poster").order_by("-created_at")
	elif section == "post-approvals":
		context["pending_jobs"] = (
			Job.objects.filter(status=Job.Status.PENDING)
			.select_related("poster")
			.order_by("-created_at")
		)
	elif section == "approvals":
		context["applications"] = (
			JobApplication.objects.select_related("job", "applicant", "decided_by")
			.order_by("-created_at")
		)
	elif section == "transactions":
		transactions = Transaction.objects.select_related("recipient", "job").order_by("-created_at")
		aggregates = transactions.aggregate(total_amount=Sum("amount"))
		subscription_total = SubscriptionLedgerEntry.objects.aggregate(total_amount=Sum("amount"))
		context.update(
			{
				"transactions": transactions,
				"total_amount": aggregates.get("total_amount") or 0,
				"subscription_total": subscription_total.get("total_amount") or 0,
			}
		)
	elif section == "subscribers":
		entries = SubscriptionLedgerEntry.objects.select_related("user").order_by("-created_at")
		plan_order = [
			UserProfile.SubscriptionPlan.ONE_MONTH,
			UserProfile.SubscriptionPlan.SIX_MONTHS,
			UserProfile.SubscriptionPlan.ONE_YEAR,
		]
		plan_sections = []
		for plan_key in plan_order:
			plan_entries = entries.filter(plan=plan_key)
			plan_total = plan_entries.aggregate(total_amount=Sum("amount"))
			plan_sections.append(
				{
					"plan": plan_key,
					"label": UserProfile.SUBSCRIPTION_DETAILS.get(plan_key, {}).get(
						"label",
						UserProfile.SubscriptionPlan(plan_key).label,
					),
					"entries": plan_entries,
					"total": plan_total.get("total_amount") or 0,
				}
			)
		overall_total = entries.aggregate(total_amount=Sum("amount"))
		context.update(
			{
				"plan_sections": plan_sections,
				"subscription_total": overall_total.get("total_amount") or 0,
			}
		)
	elif section == "notifications":
		notifications = (
			Notification.objects.filter(user=request.admin_user, is_staff_only=True)
			.order_by("-created_at")
		)
		unread_ids = list(notifications.filter(is_read=False).values_list("id", flat=True))
		if unread_ids:
			Notification.objects.filter(id__in=unread_ids).update(is_read=True)
		context["notifications"] = notifications
	return render(request, "adminpanel/dashboard.html", context)


@staff_required
@require_POST
def delete_user(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	if user == request.admin_user:
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
	job = application.job
	if action == "approve" and job.is_filled and application.status != JobApplication.Status.APPROVED:
		messages.error(request, "This job already has a selected candidate.")
		return _redirect_to_section("approvals")
	application.status = (
		JobApplication.Status.APPROVED if action == "approve" else JobApplication.Status.REJECTED
	)
	application.decided_by = request.admin_user
	application.decision_at = timezone.now()
	application.save()
	if application.status == JobApplication.Status.APPROVED and not job.is_filled:
		job.is_filled = True
		job.filled_at = timezone.now()
		job.save(update_fields=["is_filled", "filled_at"])
	messages.success(request, f"Application marked as {application.get_status_display().lower()}.")
	return _redirect_to_section("approvals")


@staff_required
@require_POST
def handle_job_post_status(request, job_id):
	job = get_object_or_404(Job, pk=job_id)
	action = request.POST.get("action")
	if action == "approve":
		job.status = Job.Status.APPROVED
		job.approved_at = timezone.now()
		job.approved_by = request.admin_user
		job.save(update_fields=["status", "approved_at", "approved_by"])
		Notification.objects.create(
			user=job.poster,
			message=(
				f"Good news! '{job.work_title}' is live and visible to every Jobflick user."
			),
			link=reverse("job_list"),
		)
		messages.success(request, f"'{job.work_title}' is now live for users.")
	elif action == "delete":
		Notification.objects.create(
			user=job.poster,
			message=(
				f"'{job.work_title}' was removed by the admin team. Update the details and submit again if needed."
			),
		)
		job.delete()
		messages.info(request, "Job removed permanently.")
	else:
		messages.error(request, "Invalid action.")
	return _redirect_to_section("post-approvals")


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


@staff_required
@require_POST
def delete_notification(request, pk):
	notification = get_object_or_404(
		Notification,
		pk=pk,
		user=request.admin_user,
		is_staff_only=True,
	)
	notification.delete()
	messages.success(request, "Notification removed.")
	return _redirect_to_section("notifications")
