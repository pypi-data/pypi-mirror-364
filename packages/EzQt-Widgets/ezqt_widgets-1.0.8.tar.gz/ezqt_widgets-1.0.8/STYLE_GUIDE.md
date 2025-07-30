# EzQt Widgets – Style Guide

## Sommaire

### **Inputs**
- [AutoCompleteInput](#autocompleteinput)
- [PasswordInput](#passwordinput)
- [SearchInput](#searchinput)
- [TabReplaceTextEdit](#tabreplacetextedit)

### **Labels**
- [ClickableTagLabel](#clickabletaglabel)
- [HoverLabel](#hoverlabel)
- [IndicatorLabel](#indicatorlabel)

### **Boutons**
- [DateButton](#datebutton)
- [LoaderButton](#loaderbutton)
- [IconButton](#iconbutton)

### **Divers**
- [CircularTimer](#circulartimer)
- [OptionSelector](#optionselector)
- [ToggleIcon](#toggleicon)
- [ToggleSwitch](#toggleswitch)

---

Ce document définit les conventions de style (QSS) pour les widgets custom du projet EzQt Widgets.

## Principes généraux
- Utiliser des couleurs, bordures et arrondis cohérents pour tous les widgets.
- Privilégier les sélecteurs QSS spécifiques pour chaque composant custom.
- Centraliser les couleurs et espacements pour faciliter la maintenance.

---

### AutoCompleteInput
[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
AutoCompleteInput {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px 4px 4px 4px;
    selection-color: #ffffff;
    selection-background-color: #0078d4;
}
AutoCompleteInput:hover {
    background-color: #2d2d2d;
    border: 1px solid #666666;
    border-radius: 4px 4px 4px 4px;
}
AutoCompleteInput:focus {
    background-color: #2d2d2d;
    border: 1px solid #0078d4;
    border-radius: 4px 4px 4px 4px;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.

---

### PasswordInput
[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
PasswordInput QWidget {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px 4px 4px 4px;
}

/* Champ de saisie */
PasswordInput QLineEdit {
    background-color: transparent;
    border: none;
    border-radius: 4px 4px 4px 4px;
    padding: 0px 4px 4px 4px;
    selection-color: #ffffff;
    selection-background-color: #0078d4;
}
PasswordInput QLineEdit:hover {
    background-color: transparent;
    border: none;
    border-radius: 4px 4px 4px 4px;
}
PasswordInput QLineEdit:focus {
    background-color: transparent;
    border: none;
    border-radius: 4px 4px 4px 4px;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Le padding à droite est géré automatiquement pour l'icône.
- Les propriétés de type sont automatiquement définies dans le code.

---

### SearchInput
[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
SearchInput {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px 4px 4px 4px;
    selection-color: #ffffff;
    selection-background-color: #0078d4;
}
SearchInput:hover {
    background-color: #2d2d2d;
    border: 1px solid #666666;
    border-radius: 4px 4px 4px 4px;
}
SearchInput:focus {
    background-color: #2d2d2d;
    border: 1px solid #0078d4;
    border-radius: 4px 4px 4px 4px;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.

---

### TabReplaceTextEdit
[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
TabReplaceTextEdit {
    background-color: #2d2d2d;
    border-radius: 5px;
    padding: 10px;
    selection-color: #ffffff;
    selection-background-color: #0078d4;
}
TabReplaceTextEdit QScrollBar:vertical {
    width: 8px;
}
TabReplaceTextEdit QScrollBar:horizontal {
    height: 8px;
}
TabReplaceTextEdit:hover {
    border: 2px solid #666666;
}
TabReplaceTextEdit:focus {
    border: 2px solid #0078d4;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les scrollbars sont personnalisées pour une meilleure intégration.
- Les propriétés de type sont automatiquement définies dans le code.

---

### ClickableTagLabel
[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal - état non sélectionné */
ClickableTagLabel[status="unselected"] {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px 4px 4px 4px;
}

/* Widget principal - état sélectionné */
ClickableTagLabel[status="selected"] {
    background-color: #2d2d2d;
    border: 1px solid #0078d4;
    border-radius: 4px 4px 4px 4px;
}

/* Label interne */
ClickableTagLabel QLabel {
    background-color: transparent;
    border: none;
    border-radius: 4px 4px 4px 4px;
    color: #ffffff;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.
- Utiliser la propriété `status_color` pour personnaliser la couleur du texte sélectionné.

---

### HoverLabel
[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
HoverLabel {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px 4px 4px 4px;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.

---

### IndicatorLabel
[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
IndicatorLabel {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px 4px 4px 4px;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.

---

### DateButton
[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
DateButton {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px 4px 4px 4px;
    selection-color: #ffffff;
    selection-background-color: #0078d4;
}
DateButton:hover {
    background-color: #2d2d2d;
    border: 1px solid #666666;
    border-radius: 4px 4px 4px 4px;
}
DateButton:focus {
    background-color: #2d2d2d;
    border: 1px solid #0078d4;
    border-radius: 4px 4px 4px 4px;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.

---

### LoaderButton
[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
LoaderButton {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px 4px 4px 4px;
    selection-color: #ffffff;
    selection-background-color: #0078d4;
}
LoaderButton:hover {
    background-color: #2d2d2d;
    border: 1px solid #666666;
    border-radius: 4px 4px 4px 4px;
}
LoaderButton:focus {
    background-color: #2d2d2d;
    border: 1px solid #0078d4;
    border-radius: 4px 4px 4px 4px;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.

---

### IconButton
[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
IconButton {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px 4px 4px 4px;
    selection-color: #ffffff;
    selection-background-color: #0078d4;
}
IconButton:hover {
    background-color: #2d2d2d;
    border: 1px solid #666666;
    border-radius: 4px 4px 4px 4px;
}
IconButton:focus {
    background-color: #2d2d2d;
    border: 1px solid #0078d4;
    border-radius: 4px 4px 4px 4px;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.

---

### CircularTimer

[⬆️ Retour en haut](#sommaire)

**Note :** Ce widget n'utilise pas de QSS pour la personnalisation. Les couleurs et l'apparence sont contrôlées via les propriétés Python :

- `ring_color` : Couleur de l'arc de progression (QColor, str)
- `node_color` : Couleur du centre (QColor, str)
- `ring_width_mode` : Épaisseur de l'arc ("small", "medium", "large")
- `pen_width` : Épaisseur personnalisée (prioritaire sur ring_width_mode)

**Exemple d'utilisation :**
```python
timer = CircularTimer(
    ring_color="#0078d4",
    node_color="#ffffff", 
    ring_width_mode="medium",
    loop=True
)
```

---

### OptionSelector

[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
OptionSelector {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px 4px 4px 4px;
}

/* Sélecteur animé */
OptionSelector [type="OptionSelector_Selector"] {
    background-color: #0078d4;
    border: none;
    border-radius: 4px 4px 4px 4px;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.
- Le sélecteur animé s'adapte automatiquement à l'option sélectionnée.

---

### ToggleIcon

[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
ToggleIcon {
    background-color: #2d2d2d;
    border: none;
    border-radius: 4px 4px 4px 4px;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.
- Le widget utilise soit des icônes personnalisées, soit des triangles dessinés par paintEvent.

---

### ToggleSwitch

[⬆️ Retour en haut](#sommaire)

<details>
<summary>Voir le QSS</summary>

```css
/* Widget principal */
ToggleSwitch {
	background-color: $_main_border;
	border: 2px solid $_accent_color1;
	border-radius: 12px;
}

ToggleSwitch:hover {
	border: 2px solid $_accent_color4;
}
```
</details>

- Adapter les couleurs selon la charte graphique de votre application.
- Les propriétés de type sont automatiquement définies dans le code.
- Le widget utilise des variables CSS pour les couleurs ($_main_border, $_accent_color1, $_accent_color4).

---

## Bonnes pratiques

[⬆️ Retour en haut](#sommaire)

- Les propriétés de type sont automatiquement définies dans le code des widgets.
- Documenter chaque section de QSS dans ce fichier.
- Tester l'apparence sur différents OS et thèmes Qt.
- Utiliser des couleurs cohérentes pour la sélection (selection-color et selection-background-color). 

