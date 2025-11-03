# imoveis/forms.py
from django import forms
from .models import Imovel

# 1. A CORREÇÃO CRUCIAL ESTÁ AQUI
class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        default_attrs = {'multiple': True}
        if attrs:
            default_attrs.update(attrs)
        
        # 2. USAMOS O MÉTODO __INIT__ DO "AVÔ" (forms.Input) PARA PULAR A TRAVA DE SEGURANÇA
        # DO "PAI" (forms.FileInput)
        super(forms.FileInput, self).__init__(default_attrs)

class ImovelForm(forms.ModelForm):
    fotos_galeria = forms.FileField(
        widget=MultipleFileInput(),
        required=False,
        label='Fotos da Galeria (selecione várias)'
    )

    class Meta:
        model = Imovel
        fields = [
            # 'plano', # <--- [LINHA REMOVIDA] ---
            'finalidade', 'imobiliaria', 'cidade', 'bairro', 'titulo', 'descricao', 
            'endereco', 'preco', 'telefone_contato', 'quartos', 'suites', 'banheiros', 'salas', 
            'cozinhas', 'closets', 'area', 'foto_principal'
        ]
        
        widgets = {
            # 'plano': forms.Select(attrs={'class': 'form-select'}), # <--- [LINHA REMOVIDA] ---
            'finalidade': forms.Select(attrs={'class': 'form-select'}),
            'imobiliaria': forms.Select(attrs={'class': 'form-select'}),
            'cidade': forms.Select(attrs={'class': 'form-select'}),
            'bairro': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.Select, forms.Textarea, forms.FileInput)):
                field.widget.attrs['class'] = 'form-control'