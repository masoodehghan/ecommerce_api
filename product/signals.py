from django.dispatch import receiver
from django.db.models.signals import pre_save
from .models import Product, Category
from django.utils.text import slugify
import random


@receiver(pre_save, sender=Product)
def create_slug_product(sender, instance=None, **kwargs):
    if not instance.slug:
        instance.slug = create_unique_slug(instance)
    elif instance.name != sender.objects.get(id=instance.id).name:
        instance.slug = create_unique_slug(instance)


@receiver(pre_save, sender=Category)
def create_slug_category(sender, instance=None, **kwargs):
    if not instance.slug:
        instance.slug = create_unique_slug(instance)
    elif instance.name != sender.objects.get(id=instance.id).name:
        instance.slug = create_unique_slug(instance)


def create_unique_slug(instance):

    slug = slugify(instance.name)
    sender = instance.__class__

    query_set = sender.objects.filter(slug=slug)
    if query_set.exists():
        random_list = random.sample(range(97, 123), 4)
        random_str = ''.join(map(chr, random_list))

        new_slug = f"{slug}-{random_str}"
        slug = new_slug
    return slug
