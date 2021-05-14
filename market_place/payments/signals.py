from django.db.models.signals import post_save
from django.dispatch import receiver

from auth_.models import User
from common.constants import PENDING, DONE
from payments.models import Order, Transaction


@receiver(post_save, sender=Transaction)
def set_assignee(sender, instance, created, **kwargs):
    if created:
        Order.objects.create(transaction=instance)


def save_assignee(instance, assignee):
    instance.assignee = assignee
    instance.status = PENDING
    instance.save()


@receiver(post_save, sender=Order)
def set_assignee(sender, instance, created, **kwargs):
    if created:
        assignee_min_tasks = User.objects.count_orders().first()
        director = User.objects.directors().first()
        if assignee_min_tasks:
            save_assignee(instance, assignee_min_tasks)
        elif director:
            save_assignee(instance, director)


@receiver(post_save, sender=Order)
def completion_check(sender, instance, created, **kwargs):
    if instance.status == DONE:
        instance.availability.amount -= 1
        instance.save()