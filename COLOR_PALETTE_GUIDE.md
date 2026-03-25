# 🎨 RaceHub Color Palette Refactoring Guide

## Overview
RaceHub has been refactored from a multicolor design to a professional, monochromatic color scheme centered on electric blue and neutral tones.

---

## 🎯 Color Palette

### Primary Color (Brand/Interactive Elements)
- **Electric Blue**: `#007AFF`
- **Usage**: Active tabs, primary buttons, links, icons for primary actions, borders in active states
- **Hover State**: `#0063d6` (darker blue)

### Background Colors
- **Page Background**: `#F8FAFC` (ultra light gray/slate-50)
- **Container/Card Background**: `#FFFFFF` (pure white)
- **Modal Background**: `#FFFFFF` (pure white)

### Neutral Gray Tones
- **Darkest Text (Headings)**: `#1e293b` (slate-900)
- **Primary Text**: `#334155` (slate-700)
- **Secondary Text**: `#475569` (slate-600)
- **Tertiary Text**: `#64748b` (slate-500)
- **Borders & Dividers**: `#e2e8f0` (slate-200)
- **Light Backgrounds/Disabled**: `#f1f5f9` (slate-100)
- **Input Borders**: `#cbd5e1` (slate-300)

### Accent Color (Exception)
- **Red (Logout Only)**: `#dc2626` (red-600)
- **Usage**: Logout button text/icon only

---

## 📱 Component Styling

### A. Navigation Buttons (Top Navigation)

#### Profile Button (`btn-perfil`)
```css
.btn-perfil {
    background: #f1f5f9;      /* Light gray background */
    color: #1e293b;            /* Dark text */
}
```
- **Icon**: Electric Blue (`#007AFF`)

#### Share Button (`btn-share`)
```css
.btn-share {
    background: #f1f5f9;      /* Light gray background */
    color: #1e293b;            /* Dark text */
}
```
- **Icon**: Electric Blue (`#007AFF`)

#### Logout Button (`btn-logout`)
```css
.btn-logout {
    background: #f1f5f9;       /* Light gray background */
    color: #1e293b;            /* Dark text */
}
```
- **Icon**: Red (`#dc2626`) — Only icon is red, not the button

#### Hover State (All Nav Buttons)
```css
.btn-nav:hover {
    background: #e2e8f0;       /* Slightly darker gray */
}
```

---

### B. View Tabs (Table/Calendar Toggle)

#### Inactive Tab
```css
.toggle-btn {
    background: transparent;
    color: #64748b;            /* Neutral gray text */
}
```

#### Active Tab
```css
.toggle-btn.active {
    color: #007AFF;            /* Electric blue text */
    /* Blue underline appears via ::after pseudo-element */
}

.toggle-btn.active::after {
    background: #007AFF;       /* Electric blue underline */
}
```

#### Container
```css
.toggle-container {
    background: #FFFFFF;       /* White background */
    border: 1px solid #e2e8f0; /* Light gray border */
}
```

---

### C. Search & Add Section

#### Search Input
```css
input[type="text"] {
    background: #FFFFFF;       /* White background */
    border: 1px solid #cbd5e1; /* Light gray border */
    color: #1e293b;            /* Dark text */
}

input[type="text"]:focus {
    border-color: #007AFF;                    /* Electric blue on focus */
    box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}
```

#### Add Button (Primary Action)
```css
button {
    background: #007AFF;       /* Electric blue (solid block) */
    color: white;              /* White text */
}

button:hover {
    background: #0063d6;       /* Darker electric blue */
}

button:disabled {
    background: #cbd5e1;       /* Gray when disabled */
    color: inherit;
}
```

#### Container
```css
.search-box {
    background: #FFFFFF;       /* White background */
    border: 1px solid #e2e8f0; /* Light gray border */
}
```

---

### D. Race Table

#### Header Row
```css
th {
    background-color: #FFFFFF; /* White background */
    color: #475569;            /* Secondary text color */
    border-bottom: 2px solid #e2e8f0;
}
```

#### Data Cells
```css
td {
    color: #334155;            /* Primary text color */
    border-bottom: 1px solid #e2e8f0;
}
```

#### Row Container
```css
tr {
    background: #FFFFFF;       /* White row background */
}
```

#### Status Badge (e.g., "FINALIZADA")
```css
.badge {
    background: #f1f5f9;       /* Very light gray pill */
    color: #475569;            /* Gray text */
}
```

##### Specific Status States
```css
.abierta {
    background: #f0f8ff;       /* Light blue tint */
    color: #007AFF;            /* Electric blue text */
}

.cerrada, .pendiente, .finalizada {
    background: #f1f5f9;       /* Light gray */
    color: #475569;            /* Gray text */
}
```

#### Action Buttons (Medal & Delete Icons)
```css
.btn-eliminar {
    background: #f1f5f9;       /* Light gray circular background */
    color: #007AFF;            /* Electric blue icon */
    border-radius: 50%;        /* Perfectly circular */
    width: 36px;
    height: 36px;
}

.btn-eliminar:hover {
    background: #e2e8f0;       /* Slightly darker gray */
}
```

---

### E. Loading Spinner

```css
.spinner {
    border-color: rgba(0,0,0,0.1);
    border-top-color: #007AFF; /* Electric blue spinner */
}
```

---

### F. Modals & Dialogs

#### Modal Container
```css
div {
    background: #FFFFFF;       /* White modal content */
}
```

#### Modal Headers
```css
h2 {
    color: #1e293b;            /* Dark heading text */
}
```

#### Modal Text
```css
p {
    color: #475569;            /* Secondary text */
}
```

#### Modal Buttons
- **Primary (Confirm)**: `background: #007AFF; color: white;`
- **Secondary (Cancel)**: `background: #cbd5e1; color: #1e293b;`

#### Modal Inputs
```css
input {
    background: #FFFFFF;
    border: 1px solid #cbd5e1;
    color: #1e293b;
}

input:focus {
    border-color: #007AFF;
}
```

---

### G. Calendar View

#### Month Title
```css
.mes-titulo {
    color: #1e293b;             /* Dark text */
    border-bottom: 2px solid #007AFF; /* Electric blue underline */
}
```

#### Card Container
```css
.carrera-card {
    background: #FFFFFF;        /* White card */
    border: 1px solid #e2e8f0;  /* Light gray border */
}
```

#### Date Border
```css
.carrera-fecha {
    border-right: 2px solid #007AFF; /* Electric blue border */
}

.carrera-fecha .dia {
    color: #007AFF;             /* Electric blue date */
}

.carrera-fecha .dia-semana {
    color: #64748b;             /* Gray weekday */
}
```

#### Card Content
```css
.carrera-info h4 {
    color: #1e293b;             /* Dark heading */
}

.carrera-info p {
    color: #64748b;             /* Gray text */
}
```

#### Past Event Styling
```css
.carrera-pasada {
    background: #f8fafc;
    border-color: #e2e8f0;
    opacity: 0.7;
}
```

---

## 🔄 Mobile Responsive Adjustments

All color assignments remain consistent on mobile. The responsive design maintains:
- Same color palette
- Same component styling
- Adjusted layout only (no color changes)

---

## 📋 Migration Checklist

- [x] Navigation buttons: Ghost style with slate-100 background
- [x] Navigation icons: Electric blue for Profile & Share
- [x] Logout button: Red icon only
- [x] Toggle tabs: Active with blue underline
- [x] Search box: White background with proper borders
- [x] Add button: Solid electric blue (primary action)
- [x] Table rows: White with light gray dividers
- [x] Status badges: Light gray pills with dark text
- [x] Table action icons: Circular light gray backgrounds with blue icons
- [x] Modal styling: White backgrounds with updated button colors
- [x] Loading spinner: Electric blue
- [x] Calendar view: Proper text colors and blue accents

---

## 🎨 Color Value Reference

| Purpose | Hex Value | Name |
|---------|-----------|------|
| Primary/Brand | `#007AFF` | Electric Blue |
| Primary Hover | `#0063d6` | Dark Electric Blue |
| Page Background | `#F8FAFC` | Ultra Light Gray |
| Container/White | `#FFFFFF` | Pure White |
| Text - Dark | `#1e293b` | Slate-900 |
| Text - Primary | `#334155` | Slate-700 |
| Text - Secondary | `#475569` | Slate-600 |
| Text - Tertiary | `#64748b` | Slate-500 |
| Border/Divider | `#e2e8f0` | Slate-200 |
| Light Background | `#f1f5f9` | Slate-100 |
| Input Borders | `#cbd5e1` | Slate-300 |
| Accent Red | `#dc2626` | Red-600 |

---

## ✨ Notes

- The electric blue (`#007AFF`) is used exclusively for interactive primary elements and active states
- All secondary actions use neutral gray color scheme
- The red accent is reserved only for the logout button
- White and light gray create clean contrast without visual noise
- The design maintains accessibility with proper color contrast ratios

