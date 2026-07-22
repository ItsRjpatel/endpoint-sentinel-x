import { useState } from 'react';
import {
  ShieldOff,
  Terminal,
  RotateCcw,
  FileText,
  MoreHorizontal,
  Code,
  RefreshCw,
  ShieldCheck,
  PowerOff,
} from 'lucide-react';
import { EndpointDetails } from '../../types';

interface EndpointQuickActionsProps {
  endpoint: EndpointDetails;
}

/**
 * Presentation only — no onClick handlers wired to real mutations.
 * Hierarchy: one destructive primary action (Isolate host), a small set of
 * frequent secondary actions, and everything else tucked behind "More".
 */
export function EndpointQuickActions({ endpoint }: EndpointQuickActionsProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="flex items-center gap-2">
      {/* Primary containment action */}
      <button
        type="button"
        className="inline-flex items-center gap-2 rounded-md bg-danger px-3.5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-danger/90 focus:outline-none focus:ring-2 focus:ring-danger focus:ring-offset-2 focus:ring-offset-surface-primary transition-colors"
      >
        <ShieldOff className="h-4 w-4" aria-hidden="true" />
        <span>{endpoint.isolated ? 'Release from isolation' : 'Isolate host'}</span>
      </button>

      <div className="hidden h-6 w-px bg-border sm:block" aria-hidden="true" />

      {/* Frequent secondary actions */}
      <button
        type="button"
        className="inline-flex items-center gap-2 rounded-md border border-border bg-surface-secondary px-3 py-2 text-sm font-medium text-text-primary hover:bg-surface-secondary/70 transition-colors"
      >
        <Terminal className="h-4 w-4 text-text-muted" aria-hidden="true" />
        <span className="hidden lg:inline">Remote shell</span>
      </button>
      <button
        type="button"
        className="inline-flex items-center gap-2 rounded-md border border-border bg-surface-secondary px-3 py-2 text-sm font-medium text-text-primary hover:bg-surface-secondary/70 transition-colors"
      >
        <RefreshCw className="h-4 w-4 text-text-muted" aria-hidden="true" />
        <span className="hidden lg:inline">Sync</span>
      </button>

      {/* Overflow menu */}
      <div className="relative">
        <button
          type="button"
          onClick={() => setMenuOpen((v) => !v)}
          className="inline-flex items-center justify-center rounded-md border border-border bg-surface-secondary p-2 text-text-muted hover:bg-surface-secondary/70 hover:text-text-primary transition-colors"
          aria-haspopup="menu"
          aria-expanded={menuOpen}
          aria-label="More actions"
        >
          <MoreHorizontal className="h-4 w-4" />
        </button>

        {menuOpen && (
          <div
            role="menu"
            className="absolute right-0 z-20 mt-1.5 w-56 overflow-hidden rounded-md border border-border bg-card py-1 shadow-lg"
          >
            {[
              { icon: RotateCcw, label: 'Restart device' },
              { icon: PowerOff, label: 'Shut down device' },
              { icon: Code, label: 'Run script' },
              { icon: FileText, label: 'Collect investigation package' },
              { icon: ShieldCheck, label: 'Reassign compliance policy' },
            ].map(({ icon: Icon, label }) => (
              <button
                key={label}
                role="menuitem"
                className="flex w-full items-center gap-2.5 px-3.5 py-2 text-left text-sm text-text-secondary hover:bg-surface-secondary hover:text-text-primary transition-colors"
              >
                <Icon className="h-4 w-4 text-text-muted" aria-hidden="true" />
                {label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
