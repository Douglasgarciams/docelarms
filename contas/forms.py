# contas/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User

# --- Formulário de Cadastro (ATUALIZADO) ---
class CustomUserCreationForm(UserCreationForm):
    
    # --- [INÍCIO DA MUDANÇA] ---
    # 1. Criamos o campo de escolha que não vai para o banco (required=True)
    TIPO_CONTA_CHOICES = [
        ('PARTICULAR', 'Sou um anunciante particular'),
        ('IMOBILIARIA', 'Sou uma Imobiliária / Corretor'),
    ]
    tipo_conta = forms.ChoiceField(
        choices=TIPO_CONTA_CHOICES,
        widget=forms.RadioSelect, # Cria botões de rádio (bolinhas)
        label="Tipo de Conta",
        required=True,
    )
    # --- [FIM DA MUDANÇA] ---

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
        
        # --- [INÍCIO DA CORREÇÃO] ---
        # 2. Reordena os campos para 'tipo_conta' aparecer primeiro
        # E corrige os nomes dos campos de senha
        field_order = [
            'tipo_conta',
            'first_name',
            'last_name',
            'email',
            'username',
            'password1', # <-- CORRIGIDO
            'password2', # <-- CORRIGIDO
        ]
        
        # Recria a ordem dos campos
        new_order = {}
        for key in field_order:
            if key in self.fields:
                new_order[key] = self.fields[key]
        
        # Adiciona campos restantes (caso algum tenha sido esquecido)
        for key, field in self.fields.items():
            if key not in new_order:
                new_order[key] = field
                
        self.fields = new_order
        # --- [FIM DA CORREÇÃO] ---


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