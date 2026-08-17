# assets

Identidade visual do Fincheck. O Flet serve esta pasta automaticamente, então
`assets/logo_wordmark.png` é referenciado no código como
`ft.Image(src="logo_wordmark.png")`.

## Arquivos

| Arquivo | Tamanho | Uso |
|---|---|---|
| `icon.png` | 1024x1024 | Ícone do app (lido pelo `flet build apk`) |
| `icon_monogram.png` | 1024x1024 | Alternativa: só o "F". Veja a nota abaixo |
| `splash_android.png` | 1152x1152 | Splash screen (tema claro) |
| `splash_android_dark.png` | 1152x1152 | Splash screen (tema escuro) |
| `logo_wordmark.png` | 1899x341 | Logotipo com fundo transparente, usado na tela de Perfil |
| `banner.png` | 2126x834 | Logotipo + slogan, para divulgação |

## Cores da marca

Amostradas diretamente da arte original e replicadas em
`views/components/theme.py`:

| Token | HEX |
|---|---|
| Verde Fincheck | `#104535` |
| Dourado Fincheck | `#CDAD56` |

## Como estes arquivos foram gerados

A arte original (`Logo.png`) era um mockup: o ícone aparecia sobre fundo branco,
com sombra projetada e textura de tecido. Recortar direto trazia cantos claros e,
ao tentar limpá-los por saturação, a textura do tecido virava manchas.

Por isso o `icon.png` é gerado a partir da arte **chapada** do banner: o
logotipo é recomposto sobre o verde sólido usando uma máscara de alfa
proporcional à distância do fundo. Isso elimina a vinheta e a textura, preserva
o antialiasing das bordas e mantém as cores exatas da marca — além de ficar
nítido nos tamanhos pequenos (48dp), onde a textura viraria ruído.

## Nota sobre o ícone no Android

O `icon.png` usa o logotipo por extenso, como você pediu. Vale saber de uma
limitação: a partir do Android 8 os launchers aplicam uma máscara adaptativa
(círculo, squircle etc.) e cortam as bordas do ícone. Um logotipo horizontal e
estreito é o formato que mais sofre com isso — em launchers de máscara circular
as pontas do "F" e do "k" podem ser aparadas, e o texto fica pequeno.

Se quiser trocar pelo monograma, que resolve os dois problemas:

```bash
copy meu_app_financeiro\assets\icon_monogram.png meu_app_financeiro\assets\icon.png
```

Depois é só rodar `gerar_apk.bat` de novo.
