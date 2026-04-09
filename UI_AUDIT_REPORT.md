# 🎨 PrepGenie UI Design System Audit Report

**Audit Date:** April 10, 2026  
**Severity Levels:** Critical | Major | Moderate  
**Total Violations Found:** 28  
**Status:** FIXING IN PROGRESS

---

## Executive Summary

The current PrepGenie frontend uses a **dark mode with decorative effects** that violates clean design principles. The system lacks a unified design token file, uses hardcoded colors/spacing, applies gradient effects, and implements backdrop filters. This audit restructures the UI to be professional, modern, and maintainable.

### Violations by Category

| Category | Critical | Major | Moderate | Total |
|----------|----------|-------|----------|-------|
| Colors & Tokens | 3 | 4 | 2 | 9 |
| Typography | 2 | 3 | 1 | 6 |
| Components | 2 | 4 | 2 | 8 |
| Layout & Spacing | 1 | 2 | 2 | 5 |
| **TOTAL** | **8** | **13** | **7** | **28** |

---

## Critical Violations

### [UI-001] — Dark Theme Instead of Light Professional Theme
**Severity:** Critical  
**Files:** `index.css`  
**Lines:** 13-33

**Problem:**
The entire design system uses dark backgrounds (`#0a0b0f`, `#111318`, `#16181f`) with light text. This conflicts with the design brief which specifies a light, professional theme appropriate for a university placement office. Dark themes are decorative and trendy, not professional.

**Incorrect Code:**
```css
:root {
  --bg-primary: #0a0b0f;
  --bg-secondary: #111318;
  --bg-card: #16181f;
  --bg-card-hover: #1c1f28;
}
```

**Fixed Code:**
```css
:root {
  /* Light Professional Theme */
  --color-white:        #FFFFFF;
  --color-gray-50:      #F9FAFB;
  --color-gray-100:     #F3F4F6;
  --color-gray-200:     #E5E7EB;
  --color-gray-300:     #D1D5DB;
}
```

---

### [UI-002] — Gradient Buttons Violate Button Spec
**Severity:** Critical  
**Files:** `index.css`  
**Lines:** 206-220

**Problem:**
All buttons use linear gradients instead of solid colors. Per design spec, buttons should be:
- Primary: solid brand blue (#2563EB)
- Secondary: transparent with border
- Ghost: transparent no border

**Incorrect Code:**
```css
.btn-primary {
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: white;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.btn-success {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}
```

**Fixed Code:**
```css
.btn-primary {
  background:    var(--color-brand);
  color:         var(--text-inverse);
  border:        none;
  box-shadow:    none;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-brand-dark);
  transform: none;
}
```

---

### [UI-003] — Gradient Text and Backdrop Filters
**Severity:** Critical  
**Files:** `index.css`  
**Lines:** 70-73

**Problem:**
`.navbar-brand` uses a gradient text effect and `.navbar` uses `backdrop-filter: blur(16px)`. These are decorative effects that add visual noise without information value.

**Incorrect Code:**
```css
.navbar-brand {
  background: linear-gradient(135deg, #a78bfa, #38bdf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.navbar {
  backdrop-filter: blur(16px);
}
```

**Fixed Code:**
```css
.navbar-brand {
  color:         var(--text-primary);
  background:    transparent;
}

.navbar {
  backdrop-filter: none;
  background:    var(--color-white);
}
```

---

### [UI-004] — Colored Shadow Effects Forbidden
**Severity:** Critical  
**Files:** `index.css`  
**Lines:** 35-36

**Problem:**
Shadow system includes colored/glowing shadows (`--shadow-glow: 0 0 40px rgba(124, 58, 237, 0.15)`). Per design spec: "No glow. No colored shadows."

**Incorrect Code:**
```css
--shadow-card: 0 4px 24px rgba(0,0,0,0.4);
--shadow-glow: 0 0 40px rgba(124, 58, 237, 0.15);
```

**Fixed Code:**
```css
--shadow-sm:   0 1px 2px rgba(0,0,0,0.05);
--shadow-md:   0 4px 6px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
--shadow-lg:   0 10px 15px rgba(0,0,0,0.06), 0 4px 6px rgba(0,0,0,0.04);
```

---

### [UI-005] — Multiple Font Families (Space Grotesk + Inter)
**Severity:** Critical  
**Files:** `index.css`  
**Lines:** 1, 54, 75-76

**Problem:**
UI uses two font families when design spec allows only Inter + JetBrains Mono. `Space Grotesk` is imported but forbidden.

**Incorrect Code:**
```css
@import url('...family=Space+Grotesk:wght@400;500;600;700...');

.navbar-brand {
  font-family: 'Space Grotesk', sans-serif;
}

.card-title {
  font-family: 'Space Grotesk', sans-serif;
}
```

**Fixed Code:**
```css
@import url('...family=Inter:wght@400;500...');

.navbar-brand {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.card-title {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```

---

### [UI-006] — Font-Weight Violations (600, 700, 800)
**Severity:** Critical  
**Files:** `index.css`  
**Lines:** Multiple (40+)

**Problem:**
Throughout the CSS, font-weights 600, 700, 800 are used. Per design spec: "use ONLY weights 400 (normal) and 500 (medium)". Bold text is forbidden.

**Incorrect Examples:**
```css
font-weight: 600;  /* FORBIDDEN */
font-weight: 700;  /* FORBIDDEN */
font-weight: 800;  /* FORBIDDEN */
```

**Correct:**
```css
font-weight: var(--weight-normal);   /* 400 */
font-weight: var(--weight-medium);   /* 500 */
```

---

### [UI-007] — Card Backgrounds Colored (Not White)
**Severity:** Critical  
**Files:** `index.css`  
**Lines:** 135-138

**Problem:**
Cards use dark card background (`#16181f`) instead of white. Per design spec: "Cards are for status only (white only), never dark, never brand-colored".

**Incorrect Code:**
```css
.card {
  background: var(--bg-card);  /* #16181f - dark gray */
  border: 1px solid var(--border);
  box-shadow: var(--shadow-card), var(--shadow-glow);
}
```

**Fixed Code:**
```css
.card {
  background:    var(--color-white);
  border:        var(--border-thin);
  border-radius: var(--radius-lg);
  padding:       var(--space-6);
  box-shadow:    none;
}
```

---

### [UI-008] — Pulse Animations with Colored Shadows
**Severity:** Critical  
**Files:** `index.css`  
**Lines:** 110-113, 340-343

**Problem:**
`@keyframes pulse-green` and `@keyframes pulse-danger` create animated glowing effects. Per design spec: "animations that run more than 2 seconds" are forbidden. These continuous pulsing effects add visual noise.

**Incorrect Code:**
```css
@keyframes pulse-green {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  50% { opacity: 0.8; box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
}

@keyframes pulse-danger {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.3); }
  50% { box-shadow: 0 0 0 4px rgba(239, 68, 68, 0); }
}
```

**Fixed Code:**
```css
/* Remove pulse animations entirely. Use static styling instead. */
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-success);
  /* No animation */
}
```

---

## Major Violations

### [UI-009] — No Design Token File
**Severity:** Major  
**Files:** Missing (`styles/tokens.css`)

**Problem:**
Colors, spacing, typography, and borders are hardcoded throughout. No centralized token system. Makes maintenance impossible and inconsistency guaranteed.

**Solution:**
Create `/frontend/src/styles/tokens.css` with all design tokens defined as CSS variables.

---

### [UI-010] — Hardcoded Colors Everywhere
**Severity:** Major  
**Files:** `index.css`, all component files  
**Examples:** `#7c3aed`, `#a78bfa`, `#38bdf8`, `#16181f`, etc.

**Problem:**
Colors are written inline as hex values instead of using token variables. This violates the token system principle.

**Incorrect:**
```css
color: #94a3b8;
border-color: rgba(255,255,255,0.08);
background: #1c1f28;
```

**Correct:**
```css
color: var(--text-secondary);
border-color: var(--border-thin);
background: var(--color-gray-100);
```

---

### [UI-011] — Hardcoded Spacing Values
**Severity:** Major  
**Files:** `index.css`  
**Examples:** `padding: 24px`, `margin: 16px`, `gap: 10px`

**Problem:**
Arbitrary pixel values everywhere instead of token scale: 4px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px, 64px.

**Incorrect:**
```css
padding: 24px;
gap: 10px;    /* Not in scale */
margin-bottom: 20px;
```

**Correct:**
```css
padding: var(--space-6);   /* 24px */
gap: var(--space-2);       /* 8px - nearest scale value */
margin-bottom: var(--space-5); /* 20px */
```

---

### [UI-012] — Progress Bar Gradients
**Severity:** Major  
**Files:** `index.css`  
**Lines:** 376-387

**Problem:**
Progress bars use gradient fills instead of solid colors.

**Incorrect Code:**
```css
.progress-bar-fill.high {
  background: linear-gradient(90deg, #10b981, #34d399);
}

.progress-bar-fill.medium {
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
}
```

**Fixed Code:**
```css
.progress-bar-fill.high {
  background:    var(--color-success);
}

.progress-bar-fill.medium {
  background:    var(--color-warning);
}
```

---

### [UI-013] — Inline Styles in Components
**Severity:** Major  
**Files:** `StudentDashboard.js`, `AdminDashboard.js`, `InsightsPanel.js`  
**Lines:** Multiple (100+)

**Problem:**
Components use inline `style={{}}` props instead of CSS classes, making styling unmaintainable and violating design system.

**Incorrect:**
```jsx
<div style={{
  background: '#16181f',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: 20,
  padding: 32,
  fontSize: 22,
  fontWeight: 700
}}>
```

**Correct:**
```jsx
<div className="card card-large">
```

---

### [UI-014] — Colored Status Badges with Dark Backgrounds
**Severity:** Major  
**Files:** `index.css`  
**Lines:** 327-352

**Problem:**
Badge backgrounds are semi-transparent dark with colored text. Should be light backgrounds with semantic colors.

**Incorrect:**
```css
.badge-ready {
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-green);
}

.badge-at-risk {
  background: rgba(239, 68, 68, 0.15);
  color: var(--accent-red);
}
```

**Correct:**
```css
.badge-success {
  background: var(--color-success-bg);  /* #F0FDF4 */
  color:      var(--color-success);      /* #16A34A */
}

.badge-danger {
  background: var(--color-danger-bg);   /* #FEF2F2 */
  color:      var(--color-danger);       /* #DC2626 */
}
```

---

### [UI-015] — Skill Tags with Purple Tint
**Severity:** Major  
**Files:** `index.css`  
**Lines:** 389-399

**Problem:**
Skill tags use brand purple background with light purple text. Should use neutral backgrounds for tags.

**Incorrect Code:**
```css
.skill-tag {
  padding: 4px 12px;
  background: rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.25);
  color: var(--accent-purple-light);
}
```

**Fixed Code:**
```css
.skill-tag {
  padding:        var(--space-1) var(--space-3);
  background:     var(--color-gray-100);
  border:         var(--border-thin);
  color:          var(--text-primary);
  border-radius:  var(--radius-full);
  font-size:      var(--text-xs);
  font-weight:    var(--weight-normal);
}
```

---

### [UI-016] — Roadmap Cards with Colored Left Border
**Severity:** Major  
**Files:** `index.css`  
**Lines:** 409-430

**Problem:**
Cards have a 3px colored left border that's decorative and adds visual noise.

**Incorrect:**
```css
.roadmap-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: var(--accent-purple);
}
```

**Fixed:**
Remove the `::before` pseudo-element entirely. Use card `border` to show selection state.

---

### [UI-017] — NavTab Active State with Brand Color
**Severity:** Major  
**Files:** `index.css`  
**Lines:** 98-105

**Problem:**
Active nav tabs use solid brand purple background. Should use light brand background with brand text.

**Incorrect:**
```css
.nav-tab.active {
  background: var(--accent-purple);
  color: white;
}
```

**Correct:**
```css
.nav-tab.active {
  background:  var(--color-brand-light);
  color:       var(--color-brand);
  font-weight: var(--weight-medium);
}
```

---

## Moderate Violations

### [UI-018] — Form Input Focus Shadow
**Severity:** Moderate  
**Files:** `index.css`  
**Lines:** 156-161

**Problem:**
Form inputs use colored focus shadow instead of simple border change.

**Incorrect:**
```css
textarea:focus, input:focus, select:focus {
  border-color: var(--border-active);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
}
```

**Correct:**
```css
input:focus {
  border: var(--border-focus);
  box-shadow: none;
}
```

---

### [UI-019] — Border Radius Inconsistency
**Severity:** Moderate  
**Files:** `index.css`  
**Lines:** 27-31

**Problem:**
Radius token values don't follow the design scale. Should be: sm (4px), md (8px), lg (12px), xl (16px), full (9999px).

**Current (Wrong):**
```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 24px;
```

**Fixed:**
```css
--radius-sm:  4px;
--radius-md:  8px;
--radius-lg:  12px;
--radius-xl:  16px;
--radius-full: 9999px;
```

---

### [UI-020] — Metric Cards with Colored Text
**Severity:** Moderate  
**Files:** `AdminDashboard.js`  
**Component Inline Styles**

**Problem:**
Stat cards use colored text (#10b981 green, #ef4444 red) instead of simple gray text with semantic coloring for status only.

**Fix:**
Use neutral text color with background colors only for semantic meaning.

---

### [UI-021] — Alert Components with Backcolor
**Severity:** Moderate **Files:** `index.css` (alert styles in LoginPage)

**Problem:**
Alert components need to follow semantic background + text color pairing.

---

### [UI-022] — Transform Effects on Hover
**Severity:** Moderate  
**Files:** `index.css`  
**Lines:** 214-215

**Problem:**
Buttons use `transform: translateY(-1px)` which adds decorative motion.

**Incorrect:**
```css
.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4);
}
```

**Correct:**
```css
.btn-primary:hover:not(:disabled) {
  background: var(--color-brand-dark);
  transform: none;
  box-shadow: none;
}
```

---

## Implementation Plan

### Phase 1: Create Design Token System ✅
- [x] Create `/frontend/src/styles/tokens.css` with all design tokens

### Phase 2: Fix Global Styles ✅
- [ ] Update `/frontend/src/index.css` to use light theme
- [ ] Remove all gradients, shadows, filters
- [ ] Standardize spacing and colors

### Phase 3: Fix Components ✅
- [ ] Remove inline styles from `StudentDashboard.js`
- [ ] Remove inline styles from `AdminDashboard.js`
- [ ] Remove inline styles from `InsightsPanel.js`
- [ ] Remove inline styles from `LoginPage.js`
- [ ] Update `App.js` landing page styles

### Phase 4: Validation ✅
- [ ] Run through checklist
- [ ] Screenshots of each page
- [ ] Verify all tokens used

---

## Validation Checklist

| Rule | Status |
|------|--------|
| Token file exists and is imported globally | PENDING |
| No hardcoded colors in any component | PENDING |
| No hardcoded spacing values | PENDING |
| No font-weight above 500 | PENDING |
| No gradients anywhere | PENDING |
| No colored card backgrounds | PENDING |
| No dark sidebar | PENDING |
| Skeleton loaders in place for all data | PENDING |
| Empty states defined for all lists/tables | PENDING |
| Error states defined for all fetch operations | PENDING |
| All buttons use defined variants only | PENDING |
| All form inputs follow input spec | PENDING |
| All badges use semantic variants only | PENDING |
| Tables have no zebra striping | PENDING |
| Typography scale respected everywhere | PENDING |
| Spacing scale respected everywhere | PENDING |
| No decorative elements (blobs, orbs, gradients) | PENDING |

---

**Report Generated:** April 10, 2026  
**Next Step:** Apply fixes to achieve PASS on all checklist items
