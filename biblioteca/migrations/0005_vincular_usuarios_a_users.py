from django.contrib.auth.hashers import make_password
from django.db import migrations


def vincular_usuarios(apps, schema_editor):
    Usuario = apps.get_model('biblioteca', 'Usuario')
    User = apps.get_model('auth', 'User')

    for usuario in Usuario.objects.filter(user__isnull=True):
        usuario.user = User.objects.create(
            username=f'usuario{usuario.pk}',
            email=usuario.email,
            password=make_password(None),
        )
        usuario.save(update_fields=['user'])

    for user in User.objects.filter(is_superuser=True, usuario__isnull=True):
        Usuario.objects.create(
            user=user,
            nome=user.username,
            email=user.email or f'{user.username}@bibliotech.local',
            perfil='bibliotecario',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('biblioteca', '0004_usuario_user_opcional'),
    ]

    operations = [
        migrations.RunPython(vincular_usuarios, migrations.RunPython.noop),
    ]
