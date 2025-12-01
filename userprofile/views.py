from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from jobs.models import Job, JobApplication
from adminpanel.models import SubscriptionLedgerEntry

from .forms import UserProfileForm
from .models import Notification, UserProfile
from .utils import notify_staff


@login_required
@never_cache
def dashboard_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	skills = [skill.strip() for skill in profile.skills.split(",") if skill.strip()]
	jobs = Job.objects.prefetch_related(
		Prefetch(
			"applications",
			queryset=JobApplication.objects.filter(applicant=request.user),
			to_attr="app_for_user",
		)
	)
	context = {
		"profile": profile,
		"skills": skills,
		"jobs": jobs,
		"job_count": jobs.count(),
		"hide_nav": True,
		"hide_footer": True,
	}
	return render(request, "userprofile/dashboard.html", context)


@login_required
@never_cache
def edit_profile_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	if request.method == "POST":
		form = UserProfileForm(request.POST, request.FILES, instance=profile)
		if form.is_valid():
			form.save()
			messages.success(request, "Profile updated successfully.")
			return redirect("user-dashboard")
	else:
		form = UserProfileForm(instance=profile)

	return render(
		request,
		"userprofile/edit_profile.html",
		{"form": form, "profile": profile, "hide_nav": True, "hide_footer": True},
	)


@login_required
@never_cache
def chat_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(
		request,
		"userprofile/chat_placeholder.html",
		{"profile": profile, "hide_nav": True, "hide_footer": True},
	)


@login_required
@never_cache
def activity_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(
		request,
		"userprofile/activity_placeholder.html",
		{"profile": profile, "hide_nav": True, "hide_footer": True},
	)


@login_required
@never_cache
def help_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(
		request,
		"userprofile/help_placeholder.html",
		{"profile": profile, "hide_nav": True, "hide_footer": True},
	)


@login_required
@never_cache
def dashboard_about_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(
		request,
		"userprofile/about_panel.html",
		{"profile": profile, "hide_nav": True, "hide_footer": True},
	)


@login_required
@never_cache
def dashboard_contact_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(
		request,
		"userprofile/contact_panel.html",
		{"profile": profile, "hide_nav": True, "hide_footer": True},
	)


@login_required
@never_cache
def transactions_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(
		request,
		"userprofile/transactions_placeholder.html",
		{"profile": profile, "hide_nav": True, "hide_footer": True},
	)


@login_required
@never_cache
def notifications_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	notifications = request.user.notifications.filter(is_staff_only=False)
	notifications.filter(is_read=False).update(is_read=True)
	return render(
		request,
		"userprofile/notifications.html",
		{
			"profile": profile,
			"hide_nav": True,
			"hide_footer": True,
			"notifications": notifications,
		},
	)


@login_required
@never_cache
def notification_detail_view(request, pk):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	notification = get_object_or_404(
		Notification,
		pk=pk,
		user=request.user,
		is_staff_only=False,
	)
	if not notification.is_read:
		notification.is_read = True
		notification.save(update_fields=["is_read"])
	subscription_receipt = None
	if notification.subscription_entry_id:
		entry = notification.subscription_entry
		plan_details = UserProfile.SUBSCRIPTION_DETAILS.get(entry.plan, {})
		wallet_after_purchase = max(entry.wallet_before - entry.amount, 0)
		subscription_receipt = {
			"plan": plan_details.get("label", entry.get_plan_display()),
			"amount": entry.amount,
			"wallet_before": entry.wallet_before,
			"wallet_after": wallet_after_purchase,
			"purchased_at": entry.created_at,
			"duration_days": plan_details.get("duration_days"),
		}
	return render(
		request,
		"userprofile/notification_detail.html",
		{
			"profile": profile,
			"notification": notification,
			"subscription_receipt": subscription_receipt,
			"hide_nav": True,
			"hide_footer": True,
		},
	)


@login_required
@never_cache
def delete_notification_view(request, pk):
	notification = get_object_or_404(
		Notification,
		pk=pk,
		user=request.user,
		is_staff_only=False,
	)
	if request.method == "POST":
		notification.delete()
		messages.success(request, "Notification removed.")
	return redirect("userprofile-notifications")


@login_required
@never_cache
def subscription_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	plans = UserProfile.serialize_subscription_plans()
	if request.method == "POST":
		selected_plan = request.POST.get("plan")
		plan = UserProfile.SUBSCRIPTION_DETAILS.get(selected_plan)
		if not plan:
			messages.error(request, "Please select a valid subscription plan.")
		else:
			if profile.wallet_balance < plan["price"]:
				messages.error(request, "Insufficient balance. Please top up your wallet to continue.")
			else:
					wallet_before = profile.wallet_balance
					with transaction.atomic():
						profile.wallet_balance -= plan["price"]
						profile.apply_subscription(selected_plan)
						profile.save()
						entry = SubscriptionLedgerEntry.objects.create(
							user=request.user,
							plan=selected_plan,
							amount=plan["price"],
							wallet_before=wallet_before,
						)
						Notification.objects.create(
							user=request.user,
							message=(
								f"{plan['label']} activated successfully. Expires on {profile.subscription_expires_at}."
							),
							link=reverse("userprofile-subscription-status"),
							subscription_entry=entry,
						)
						admin_link = f"{reverse('adminpanel-dashboard')}?section=subscribers"
						notify_staff(
							message=(
								f"{request.user.username} purchased {plan['label']} and {plan['price']} BDT was added to Jobflick."
							),
							link=admin_link,
						)
					messages.success(
						request,
						f"{plan['label']} activated. Your plan expires on {profile.subscription_expires_at}.",
					)
					return redirect("userprofile-subscription")
	return render(
		request,
		"userprofile/subscription.html",
		{
			"profile": profile,
			"plans": plans,
			"hide_nav": True,
			"hide_footer": True,
		},
	)


@login_required
@never_cache
def subscription_status_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	plan_details = UserProfile.SUBSCRIPTION_DETAILS.get(profile.subscription_plan)
	latest_entry = None
	wallet_after_purchase = None
	if profile.subscription_plan != UserProfile.SubscriptionPlan.NONE:
		latest_entry = (
			SubscriptionLedgerEntry.objects.filter(user=request.user, plan=profile.subscription_plan)
			.order_by("-created_at")
			.first()
		)
		if latest_entry:
			wallet_after_purchase = max(latest_entry.wallet_before - latest_entry.amount, 0)
	context = {
		"profile": profile,
		"hide_nav": True,
		"hide_footer": True,
		"plan_details": plan_details,
		"latest_entry": latest_entry,
		"wallet_after_purchase": wallet_after_purchase,
	}
	return render(request, "userprofile/subscription_status.html", context)

# Create your views here.
