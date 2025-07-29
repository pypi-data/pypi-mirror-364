# Kenshi Translator Toolkit (Beta)

⚠️ **Versão beta inicial** - Ferramenta em desenvolvimento ativo ⚠️

## Instalação
```bash
pip install kenshi-translator-toolkit
```

## Uso básico
```python
from kenshi_translator_toolkit import decode_mod, encode_mod
from kenshi_translator_toolkit.domain.entities import Data, Record, Dialog

# Extrair dados para tradução
data = decode_mod("original.mod")

# Modificar campos de tradução (exemplo)
for record in data.data:
    if record.typecode == 19:  # Diálogos
        for dialog in record.text:
            dialog.trans_text = dialog.text.upper()  # Exemplo simplificado

    # Outros campos traduzíveis
    record.trans_name = record.name.upper()
    record.trans_desc = record.description.upper()

# Gerar novo arquivo traduzido
encode_mod(data, "traduzido.mod")
```
