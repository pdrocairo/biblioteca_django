from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from biblioteca.models import Usuario


@receiver(post_save, sender=get_user_model())
def criar_bibliotecario_para_superusuario(sender, instance, created, **kwargs):
    """Superusuario novo (createsuperuser) ja nasce com perfil de bibliotecario."""
    if created and instance.is_superuser:
        Usuario.objects.create(
            user=instance,
            nome=instance.get_username(),
            email=instance.email or f'{instance.get_username()}@bibliotech.local',
            perfil=Usuario.PERFIL_BIBLIOTECARIO,
        )
