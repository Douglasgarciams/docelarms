# contas/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User

# --- Formulário de Cadastro (seu código atual, sem alterações) ---
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label='Nome', max_length=30, required=True, help_text='Obrigatório.')
    last_name = forms.CharField(label='Sobrenome', max_length=30, required=True, help_text='Obrigatório.')
    email = forms.EmailField(label='E-mail', max_length=254, required=True, help_text='Obrigatório. Digite um e-mail válido.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    # Este método traduz o label do campo 'username' que vem do Django
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Nome de Usuário'
        self.fields['username'].help_text = 'Obrigatório. 150 caracteres ou menos. Letras, dígitos e @/./+/-/_ apenas.'

# --- NOVO FORMULÁRIO PARA ATUALIZAR DADOS DO USUÁRIO ---
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label='E-mail')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Nome'
        self.fields['last_name'].label = 'Sobrenome'
        # Adiciona a classe 'form-control' a todos os campos deste formulário
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

# --- NOVO FORMULÁRIO PARA ALTERAR A SENHA ---
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Traduz os labels e adiciona a classe 'form-control'
        self.fields['old_password'].label = 'Senha Atual'
        self.fields['new_password1'].label = 'Nova Senha'
        self.fields['new_password2'].label = 'Confirmação da Nova Senha'
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})