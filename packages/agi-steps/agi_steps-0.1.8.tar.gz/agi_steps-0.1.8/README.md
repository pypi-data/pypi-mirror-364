# agi-steps

Framework para gerenciamento e execução de etapas (steps) configuráveis em Python.

## Descrição

O `agi-steps` permite organizar scripts em grupos, ativar/desativar etapas e customizar configurações via dicionários. Ideal para pipelines, automações e fluxos de trabalho flexíveis.

## Instalação

```bash
pip install agi-steps
```

## Uso Básico

### Como módulo (CLI)

```bash
python -m agi_steps
```

### Como biblioteca

```python
from agi_steps.steps import create_steps
steps_dict = {
    # Defina suas etapas aqui
}
grupos = create_steps(steps_dict)
```

## Principais Funções

- `create_steps(steps: dict) -> dict[list]`: Cria grupos de etapas a partir de um dicionário de configuração.
- `sorts_steps(steps: list[str]) -> list[str]`: Ordena etapas.
- `get_step_settings(steps: dict, step_setting: str) -> str`: Recupera configurações de uma etapa.
- `get_active_steps(steps: dict) -> list[str]`: Lista etapas ativas.
- `get_group_config(steps: dict, group_name: str) -> dict`: Retorna configurações de um grupo.
- `get_available_steps_groups(steps: dict) -> dict[list]`: Lista grupos disponíveis de etapas.
- `create_json_file(group: str, steps: list[dict], parallelism: bool = False) -> None`: Gera arquivos JSON das etapas.

## Requisitos

- Python >= 3.11
- tomli >= 2.2.1

## Licença

MIT
