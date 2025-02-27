from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name,
                    password, role='participant', profile_photo=None, **extra_fields):  # Ajout du paramètre 'profile_photo'
        if not email:
            raise ValueError('L\'adresse email est obligatoire')

        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            first_name=first_name,
            last_name=last_name, 
            role=role,
            profile_photo=profile_photo,  # Ajout du champ 'profile_photo'
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name,
                         password, profile_photo=None, **extra_fields):  # Ajout du paramètre 'profile_photo'
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(
            email, 
            first_name, 
            last_name,
            password, 
            role='organisateur', 
            profile_photo=profile_photo,  # Ajout du champ 'profile_photo'
            **extra_fields
        )
