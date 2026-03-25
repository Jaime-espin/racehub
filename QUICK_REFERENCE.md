# 🎨 RaceHub Color Refactoring - Quick Reference Card

## Color Palette at a Glance

| Usage | Hex Code | Alternate Name |
|-------|----------|----------------|
| 🎯 Primary Actions | `#007AFF` | Electric Blue |
| 🔘 Primary Hover | `#0063d6` | Dark Blue |
| 📄 Page Background | `#F8FAFC` | Ultra Light Gray |
| 🪟 Containers/Cards | `#FFFFFF` | White |
| 📝 Dark Text | `#1e293b` | Slate-900 |
| 📖 Primary Text | `#334155` | Slate-700 |
| 💬 Secondary Text | `#475569` | Slate-600 |
| 🏷️ Tertiary Text | `#64748b` | Slate-500 |
| ━━ Borders | `#e2e8f0` | Slate-200 |
| ✨ Light Buttons | `#f1f5f9` | Slate-100 |
| 🔗 Input Borders | `#cbd5e1` | Slate-300 |
| ❌ Logout Button | `#dc2626` | Red-600 |

---

## Component Color Mapping

```
┌─────────────────────────────────────────────────────┐
│ NAVIGATION BUTTONS (Top Menu)                        │
├─────────────────────────────────────────────────────┤
│ Background:  #f1f5f9 (light gray)                   │
│ Text:        #1e293b (dark)                         │
│ Icon:        #007AFF (blue) for Profile & Share     │
│             #dc2626 (red) for Logout only           │
│ Hover:      #e2e8f0 (darker gray)                   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ VIEW TABS (Table/Calendar toggle)                    │
├─────────────────────────────────────────────────────┤
│ Active:      Color: #007AFF, Underline: #007AFF     │
│ Inactive:    Color: #64748b, No underline           │
│ Container BG: #FFFFFF with #e2e8f0 border           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ SEARCH BOX & ADD BUTTON                              │
├─────────────────────────────────────────────────────┤
│ Box BG:      #FFFFFF                                │
│ Box Border:  #e2e8f0 (light gray)                   │
│ Input BG:    #FFFFFF                                │
│ Input Border: #cbd5e1 (medium gray)                 │
│ Input Focus: border:#007AFF, shadow: rgba(blue,0.1) │
│ Button BG:   #007AFF (solid blue)                   │
│ Button Text: white                                  │
│ Button Hover: #0063d6 (darker blue)                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ TABLE STYLING                                        │
├─────────────────────────────────────────────────────┤
│ Header BG:    #FFFFFF                               │
│ Header Text:  #475569                               │
│ Header Border: #e2e8f0 (bottom, 2px)                │
│ Row BG:       #FFFFFF                               │
│ Row Border:   #e2e8f0 (divider)                     │
│ Cell Text:    #334155 (dark)                        │
│ Status Badge: #f1f5f9 BG, #475569 text              │
│ Status OPEN:  #f0f8ff BG, #007AFF text              │
│ Icons Button: #f1f5f9 BG, #007AFF icon, circular    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ CALENDAR VIEW                                        │
├─────────────────────────────────────────────────────┤
│ Title:        #1e293b text, #007AFF bottom border   │
│ Card BG:      #FFFFFF                               │
│ Card Border:  #e2e8f0                               │
│ Date Border:  #007AFF (left, 2px)                   │
│ Date Number:  #007AFF (electric blue)               │
│ Day of Week:  #64748b (gray)                        │
│ Card Title:   #1e293b (dark)                        │
│ Card Text:    #64748b (gray)                        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ MODALS & DIALOGS                                     │
├─────────────────────────────────────────────────────┤
│ Background:   #FFFFFF                               │
│ Header:       #1e293b text                          │
│ Paragraph:    #475569 text                          │
│ Label:        #1e293b (bold)                        │
│ Input BG:     #FFFFFF                               │
│ Input Border: #cbd5e1                               │
│ Input Focus:  border #007AFF                        │
│ Primary Btn:  #007AFF BG, white text                │
│ Secondary Btn: #cbd5e1 BG, #1e293b text             │
│ Alert Box BG: #f0f8ff with #007AFF left border     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ LOADING & ANIMATIONS                                 │
├─────────────────────────────────────────────────────┤
│ Spinner:      #007AFF (electric blue)               │
│ Result Box:   #f0f8ff BG, #007AFF border            │
│ Expandable:   #f0f8ff BG, #007AFF border            │
└─────────────────────────────────────────────────────┘
```

---

## CSS Class Quick Reference

```css
/* Basic text colors */
.text-primary { color: #1e293b; }      /* Dark headings */
.text-secondary { color: #334155; }    /* Regular text */
.text-tertiary { color: #475569; }     /* Secondary info */
.text-light { color: #64748b; }        /* Light labels */

/* Button styles */
.btn-primary { background: #007AFF; color: white; }
.btn-secondary { background: #f1f5f9; color: #1e293b; }
.btn-danger { background: #dc2626; color: white; }

/* Background utilities */
.bg-white { background: #FFFFFF; }
.bg-light { background: #F8FAFC; }
.bg-light-form { background: #f1f5f9; }

/* Border utilities */
.border-light { border-color: #e2e8f0; }
.border-medium { border-color: #cbd5e1; }

/* Status indicators */
.status-open { background: #f0f8ff; color: #007AFF; }
.status-closed { background: #f1f5f9; color: #475569; }
```

---

## Before & After Examples

### Button
```
❌ BEFORE: background: #27ae60 (green)
✅ AFTER:  background: #007AFF (blue)
```

### Page Background
```
❌ BEFORE: background: #f4f7f6 (greenish-gray)
✅ AFTER:  background: #F8FAFC (ultra light gray)
```

### Table Header
```
❌ BEFORE: background: #f1f3f5; color: #495057
✅ AFTER:  background: #FFFFFF; color: #475569
```

### Active State
```
❌ BEFORE: background: #27ae60; color: white
✅ AFTER:  color: #007AFF; border-bottom: 2px #007AFF
```

### Modal Buttons
```
❌ Primary:   #3498db (light blue) → ✅ #007AFF (electric blue)
❌ Success:   #27ae60 (green)      → ✅ #007AFF (blue)
❌ Dismiss:   #95a5a6 (gray)       → ✅ #cbd5e1 (light gray)
```

---

## CSS Variables (Available in colors-variables.css)

```css
/* Colors */
--color-primary: #007AFF
--color-primary-hover: #0063d6
--color-primary-light: #f0f8ff
--color-bg-page: #F8FAFC
--color-bg-container: #FFFFFF
--color-text-dark-900: #1e293b
--color-text-800: #334155
--color-text-700: #475569
--color-text-600: #64748b
--color-border-200: #e2e8f0
--color-border-300: #cbd5e1
--color-bg-light-100: #f1f5f9
--color-accent-red: #dc2626

/* Usage Example */
button {
  background-color: var(--color-primary);
  color: white;
}

button:hover {
  background-color: var(--color-primary-hover);
}
```

---

## Files to Reference

| File | Purpose |
|------|---------|
| `static/styles.css` | Main stylesheet with all colors applied |
| `static/colors-variables.css` | CSS custom properties for color management |
| `COLOR_PALETTE_GUIDE.md` | Detailed component-by-component guide |
| `REFACTORING_SUMMARY.md` | Full implementation documentation |
| `templates/index.html` | HTML with updated inline styles |

---

## Troubleshooting

**Color Didn't Change?**
1. Check if it's an inline style (highest specificity)
2. Search for the old color value (e.g., #27ae60, #3498db)
3. Verify CSS file was saved
4. Clear browser cache (Ctrl+Shift+Delete)

**Button Still Wrong Color?**
1. Make sure you're editing `styles.css` not a backup
2. Check for `!important` flags
3. Verify class names match (e.g., `.btn-eliminar` not `.btn-delete`)
4. Look for inline styles in HTML that override CSS

**Text Not Visible?**
1. Check text color meets contrast ratio (AA minimum 4.5:1)
2. Verify text color is not same as background
3. Check for explicit color properties overriding

---

## Print This Guide!

Keep this reference card handy when developing new features. All colors follow the RaceHub professional electric blue and neutral gray palette.

**Last Updated**: March 2026
**Design Version**: 2.0 - Professional Monochromatic
