# Global Design Rules

See `.cursor/rules/global-design.mdc` for Cursor agent enforcement.

Design tokens live in `src/styles/design-tokens.css`.

## Color System (Strict)

- Background: `#0B0E11` (`--color-bg`)
- Brand yellow `#F0B90B`: CTA buttons + selected tab underlines only
- Earning green `#0ECB81`: earning rate data only (not buttons)
- Loss red `#F6465D`: negative PnL / sell actions only
- Greys for text and borders

## Typography

Monospace/tabular numbers via `--font-number` and `.num` utility class.

## Radii

- Buttons: 8px (`--radius-button`)
- Inputs: 12px (`--radius-input`)
- Cards: 16px (`--radius-card`)
