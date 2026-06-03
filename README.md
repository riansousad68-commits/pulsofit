# PulsoFit

Aplicativo web de produtividade para registrar e acompanhar treinos fisicos, feito com Flask, SQLite, HTML, CSS e JavaScript simples.

## Funcionalidades

- Cadastro, edicao e remocao de exercicios.
- Registro, edicao e remocao de treinos diarios.
- Historico filtrado por data.
- Dashboard com treinos da semana, repeticoes semanais e exercicio mais feito.
- Cronograma semanal para marcar os dias disponiveis para treinar.
- Nivel estilo jogo, calculado por XP acumulado.

## Como o nivel funciona

O XP e calculado pelo volume total:

```text
XP = repeticoes totais + (series totais x 5)
```

A cada 250 XP o usuario sobe de nivel.

## Estrutura

```text
app.py
database.py
requirements.txt
templates/
  base.html
  index.html
static/
  css/style.css
  js/main.js
tests/
  test_database.py
```

## Instalar e rodar

Se o comando `python3 -m venv .venv` falhar por falta de `venv` ou `pip`, instale os pacotes do Python no sistema:

```bash
sudo apt install python3-venv python3-pip
```

1. Crie um ambiente virtual:

```bash
python3 -m venv .venv
```

2. Ative o ambiente:

```bash
source .venv/bin/activate
```

3. Instale as dependencias:

```bash
pip install -r requirements.txt
```

4. Rode o projeto:

```bash
flask --app app run --debug
```

5. Abra no navegador:

```text
http://127.0.0.1:5000
```

## Rodar testes

```bash
python3 -m unittest tests.test_database -v
```
