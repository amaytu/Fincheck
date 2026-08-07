# assets

Ícones, fontes e imagens do app.

O Flet serve esta pasta automaticamente (`ft.app(..., assets_dir=...)`), então
um arquivo em `assets/logo.png` é referenciado no código como
`ft.Image(src="logo.png")`.

Convenções esperadas pelo `flet build apk`:

| Arquivo               | Uso                                  |
|-----------------------|--------------------------------------|
| `icon.png`            | Ícone do app (1024x1024 recomendado) |
| `splash_android.png`  | Splash screen no Android             |

Enquanto não houver arquivos aqui, o Flet usa os ícones padrão.
