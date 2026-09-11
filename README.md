# Pongino

## Conceito

O projeto demonstra a comunicação entre potenciômetros conectados a um Arduino e uma interface Pong distribuída por HTTP e WebSocket. A aplicação lê amostras, normaliza os valores para percentuais, cria um estado de domínio para as duas raquetes e publica atualizações em tempo real para os navegadores conectados.

A fonte serial usa streams assíncronos e reconecta à porta configurada após falhas. A fonte mock segue o mesmo contrato assíncrono, permitindo trocar o hardware sem alterar o domínio ou a API.

## Tecnologias

### Execução

- [Python 3.12+](https://docs.python.org/3.12/)
- [Tornado 6.4+](https://www.tornadoweb.org/en/stable/)
- [pyserial](https://pyserial.readthedocs.io/en/latest/)
- [pyserial-asyncio](https://pyserial-asyncio.readthedocs.io/en/latest/)
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [HTML Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [JavaScript ES Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [Tailwind CSS Play CDN](https://tailwindcss.com/docs/installation/play-cdn)
- [Arduino IDE](https://docs.arduino.cc/software/ide-v2)
- [Arduino Language Reference](https://docs.arduino.cc/language-reference/)

### Desenvolvimento

- [uv](https://docs.astral.sh/uv/)
- [Ruff](https://docs.astral.sh/ruff/)
- [Based Pyright](https://docs.basedpyright.com/latest/)
- [Taskipy](https://github.com/taskipy/taskipy)
- [Rich](https://rich.readthedocs.io/en/stable/)

As ferramentas de desenvolvimento são pytest, pytest-cov, Ruff, Based Pyright, Taskipy e Rich.

## Como executar

Instale o `uv`, copie `.env.example` para `.env` e substitua todos os placeholders descritivos por valores válidos para o ambiente e o dispositivo utilizado.

```bash
cp .env.example .env
uv sync
```

Para usar o Arduino, configure e informe `PONG_SERIAL_PORT`.

No macOS, usando a porta serial desta instalação, o `.env` pode conter:

```dotenv
PONG_SERIAL_PORT=/dev/cu.usbserial-RCBB_37NK5Y
PONG_SERIAL_BAUDRATE=115200
```

A fonte serial usa `PONG_SERIAL_TIMEOUT_SECONDS` para limitar a espera de cada linha, `PONG_SERIAL_STARTUP_DELAY_SECONDS` para aguardar a inicialização do Arduino e `PONG_SERIAL_RECONNECT_DELAY_SECONDS` para controlar o intervalo entre tentativas.

Inicie o servidor:

```bash
uv run task run
```

Acesse `http://localhost:8888` no navegador.

Para acompanhar os potenciômetros no terminal:

O diagnóstico usa Rich com tabela e barras atualizadas em tempo real. Rich pertence ao grupo `dev`, instalado por `uv sync`; esse comando de diagnóstico requer as dependências de desenvolvimento.

```bash
uv run task test-pots
```

Os comandos de qualidade são:

```bash
uv run task test
uv run task lint
uv run task format
uv run task type-check
```

O comando `type-check` executa o Based Pyright. O lint e a formatação são executados pelo Ruff.

## Observabilidade

O endpoint `GET /health` informa o modo de execução, a origem de entrada, o estado da conexão serial ou mock, os pinos configurados e a quantidade de clientes WebSocket conectados.

O servidor registra a inicialização e a finalização da fonte de entrada, tentativas de conexão serial, falhas de leitura e conexões WebSocket. O cliente WebSocket atualiza o indicador da interface e tenta reconectar com intervalo progressivo quando a conexão é encerrada.

## Estrutura

```text
├── .env.example
firmware/
├── pong_potenciometros.ino
pong/
├── config.py
├── web/
│   ├── package.json
│   ├── index.html
│   ├── tests/
│   └── static/
│       └── js/
│           ├── dom.js
│           ├── app.js
│           ├── game.js
│           ├── ui.js
│           └── websocket.js
├── domain/
│   ├── paddles/
│   │   └── state.py
│   └── potentiometer/
│       ├── entity.py
│       ├── normalization.py
│       └── reading.py
├── ports/
│   └── input_source.py
├── infra/
│   └── input/
│       ├── factory.py
│       ├── mock_source.py
│       └── serial/
│           ├── protocol.py
│           └── source.py
├── api/
│   ├── app.py
│   ├── http/
│   │   ├── health_handler.py
│   │   └── index_handler.py
│   └── websocket/
│       ├── connection_manager.py
│       ├── handler.py
│       └── serializer.py
└── cli/
    ├── pots.py
    └── server.py
tests/
├── integration/api/
└── unit/
```

## Frontend e Tailwind

A interface fica em `pong/web/`. O Tornado entrega `web/index.html` em `/` e os módulos JavaScript de `web/static/` em `/static/`. O `package.json` declara os módulos ES e o comando de testes, sem dependências npm.

> Este projeto usa o Tailwind Play CDN para simplificar o desenvolvimento e as demonstrações. Os estilos são gerados no navegador e dependem de acesso à internet. Essa abordagem é destinada ao desenvolvimento; para produção, utilize CSS compilado localmente.

O script do [Tailwind Play CDN](https://tailwindcss.com/docs/installation/play-cdn) é carregado diretamente pelo HTML. Não é necessário instalar dependências npm nem executar build ou watch. Para iniciar toda a aplicação:

```bash
uv run task run
```
