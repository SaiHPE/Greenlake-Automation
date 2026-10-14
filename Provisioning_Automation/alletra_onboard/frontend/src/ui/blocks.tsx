// The redesign's content blocks (BL-43, draft 3 mockups in frontend/mockups/kit.tsx), built on the
// HPE Design System parts. Rules they follow are in docs/UX-GUIDELINES.md.
import { Box, Button, Collapsible, Heading, Notification, Paragraph, Spinner, Text } from 'grommet';
import { Clock, FormDown, FormUp } from 'grommet-icons';
import { ReactNode, useState } from 'react';
import { StatusIcon, StepState } from './status';

export const mono = { fontFamily: 'ui-monospace, Consolas, monospace' } as const;

const NOTIFICATION_STATUS: Record<StepState, 'normal' | 'warning' | 'critical' | 'info' | 'unknown'> = {
  complete: 'normal',
  action_required: 'warning',
  failed: 'critical',
  running: 'info',
  not_started: 'unknown',
  waiting: 'unknown',
};

/** One sentence on what happened, as the Design System inline notification: icon, colour, words, time. */
export function StatusLine({
  state,
  title,
  children,
  time,
  onClose,
}: {
  state: StepState;
  title?: string;
  children?: ReactNode;
  time?: string;
  onClose?: () => void;
}) {
  const icon =
    state === 'running' ? (
      <Spinner size="xsmall" message={{ start: 'Working', end: 'Finished' }} />
    ) : state === 'waiting' ? (
      <Clock color="icon-weak" />
    ) : undefined;
  return (
    <Box flex={false}>
      <Notification
        status={NOTIFICATION_STATUS[state]}
        icon={icon}
        title={title}
        onClose={onClose}
        message={
          children || time ? (
            <Box direction="row" gap="medium" align="start" justify="between">
              <Box>{children}</Box>
              {time && (
                <Text size="small" color="text-weak" style={{ whiteSpace: 'nowrap' }}>
                  {time}
                </Text>
              )}
            </Box>
          ) : undefined
        }
      />
    </Box>
  );
}

/** The Design System empty state: a heading that says the status, one sentence on how to move on. */
export function EmptyState({ icon, title, children }: { icon?: ReactNode; title: ReactNode; children?: ReactNode }) {
  return (
    <Box direction="row" gap="medium" align="start" pad={{ vertical: 'small' }} flex={false}>
      {icon && <Box flex={false}>{icon}</Box>}
      <Box gap="xsmall">
        <Heading level={2} size="small" margin="none">
          {title}
        </Heading>
        {children && <Paragraph margin="none">{children}</Paragraph>}
      </Box>
    </Box>
  );
}

/** A surface with a heading. */
export function Panel({
  title,
  description,
  right,
  level = 2,
  children,
}: {
  title?: ReactNode;
  description?: ReactNode;
  right?: ReactNode;
  level?: 2 | 3;
  children?: ReactNode;
}) {
  return (
    <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad="medium" gap="small" flex={false}>
      {(title || right) && (
        <Box direction="row" justify="between" align="center" gap="small" wrap>
          {title && (
            <Heading level={level} size="xsmall" weight={500} margin="none">
              {title}
            </Heading>
          )}
          {right}
        </Box>
      )}
      {description && (
        <Text size="small" color="text-weak">
          {description}
        </Text>
      )}
      {children}
    </Box>
  );
}

/**
 * A section that opens on demand (the Design System collapsible child object): the whole header is
 * the control, the label is a heading, the summary stays visible when closed.
 */
export function Section({
  title,
  summary,
  right,
  level = 2,
  open: openInitially = false,
  children,
}: {
  title: ReactNode;
  summary?: ReactNode;
  right?: ReactNode;
  level?: 2 | 3;
  open?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(openInitially);
  const toggle = () => setOpen((v) => !v);
  return (
    <Box background="background-front" round="small" border={{ color: 'border-weak' }} flex={false}>
      <Box
        direction="row"
        gap="small"
        align="center"
        pad={{ horizontal: 'medium', vertical: 'xsmall' }}
        onClick={toggle}
        hoverIndicator="background-hover"
        round="small"
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggle();
          }
        }}
        aria-expanded={open}
      >
        {open ? <FormUp /> : <FormDown />}
        <Box flex direction="row" gap="small" align="baseline" wrap>
          <Heading level={level} size="xsmall" weight={500} margin="none">
            {title}
          </Heading>
          {summary && (
            <Text size="small" color="text-weak">
              {summary}
            </Text>
          )}
        </Box>
        {right && (
          // controls in the header must not toggle the section
          <Box flex={false} onClick={(e: React.MouseEvent) => e.stopPropagation()}>
            {right}
          </Box>
        )}
      </Box>
      <Collapsible open={open}>
        <Box pad={{ horizontal: 'medium', bottom: 'medium' }} gap="small">
          {children}
        </Box>
      </Collapsible>
    </Box>
  );
}

/** Finished parts of a step, one line each, with the part's own "do it again" on the right. */
export function DoneList({
  items,
}: {
  items: { text: ReactNode; state?: StepState; again?: { label: string; onClick: () => void; busy?: boolean }; detail?: ReactNode }[];
}) {
  const [open, setOpen] = useState<number | null>(null);
  return (
    <Box background="background-front" round="small" border={{ color: 'border-weak' }} flex={false}>
      {items.map((it, i) => (
        <Box key={i} border={i > 0 ? { side: 'top', color: 'border-weak' } : undefined} flex={false}>
          <Box direction="row" gap="small" align="center" pad={{ horizontal: 'medium', vertical: 'xsmall' }}>
            <StatusIcon state={it.state ?? 'complete'} />
            <Box flex direction="row" gap="small" align="center" wrap>
              <Text size="small" color="text-strong">
                {it.text}
              </Text>
              {it.detail && (
                <Button plain onClick={() => setOpen(open === i ? null : i)} aria-expanded={open === i}>
                  <Text size="small" color="text-anchor">
                    {open === i ? 'Hide detail' : 'Show detail'}
                  </Text>
                </Button>
              )}
            </Box>
            {it.again && <Button size="small" label={it.again.label} busy={it.again.busy} onClick={it.again.onClick} />}
          </Box>
          {it.detail && (
            <Collapsible open={open === i}>
              <Box pad={{ horizontal: 'medium', bottom: 'small' }} gap="small">
                {it.detail}
              </Box>
            </Collapsible>
          )}
        </Box>
      ))}
    </Box>
  );
}

/** Files, as the Design System list: one row per file with its icon, name, detail and action. */
export interface DocItem {
  icon: ReactNode;
  name: string;
  detail: string;
  action?: ReactNode;
  /** Not there yet: said in words instead of a greyed button. */
  pending?: string;
}

export function DocList({ items, label }: { items: DocItem[]; label: string }) {
  return (
    <Box
      as="ul"
      aria-label={label}
      margin="none"
      pad="none"
      background="background-front"
      round="small"
      border={{ color: 'border-weak' }}
      flex={false}
    >
      {items.map((d, i) => (
        <Box
          as="li"
          key={d.name}
          direction="row"
          gap="small"
          align="center"
          pad={{ horizontal: 'medium', vertical: 'xsmall' }}
          border={i > 0 ? { side: 'top', color: 'border-weak' } : undefined}
          style={{ listStyle: 'none' }}
        >
          <Box flex={false}>{d.icon}</Box>
          <Box flex>
            <Text size="small" weight={500} color={d.pending ? 'text-weak' : 'text-strong'}>
              {d.name}
            </Text>
            <Text size="xsmall" color="text-weak">
              {d.detail}
            </Text>
          </Box>
          {d.pending ? (
            <Text size="small" color="text-weak">
              {d.pending}
            </Text>
          ) : (
            d.action
          )}
        </Box>
      ))}
    </Box>
  );
}

/** The step's explanations, for the "About this step" panel. */
export function Guidance({ items }: { items: { title: string; body: ReactNode }[] }) {
  return (
    <Box gap="medium" flex={false}>
      {items.map((g) => (
        <Box key={g.title} gap="xxsmall" flex={false}>
          <Heading level={2} size="xsmall" weight={500} margin="none">
            {g.title}
          </Heading>
          <Text size="small">{g.body}</Text>
        </Box>
      ))}
    </Box>
  );
}

/** Commands to copy: the Design System code block, keyboard reachable, long lines wrapped. */
export function CodeBlock({ lines, label }: { lines: string[]; label: string }) {
  return (
    <Box
      as="pre"
      tabIndex={0}
      aria-label={label}
      background="background-contrast"
      round="xsmall"
      pad="small"
      margin="none"
      flex={false}
      style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}
    >
      {lines.map((c, i) => (
        <Text key={i} size="small" style={mono}>
          {c}
        </Text>
      ))}
    </Box>
  );
}

/**
 * The Design System selector: the whole card is the choice. Nothing interactive inside it, so
 * keyboard and screen readers get one control per option.
 */
export function SelectorCard({
  title,
  checked,
  disabled,
  onSelect,
  children,
}: {
  title: string;
  checked: boolean;
  disabled?: boolean;
  onSelect: () => void;
  children?: ReactNode;
}) {
  const select = disabled ? undefined : onSelect;
  return (
    <Box
      role="radio"
      aria-checked={checked}
      aria-disabled={disabled || undefined}
      tabIndex={disabled ? -1 : 0}
      pad="medium"
      round="small"
      background={checked ? 'background-selected-primary' : 'background-front'}
      border={{ color: checked ? 'border-selected' : 'border-weak', size: checked ? 'medium' : 'xsmall' }}
      onClick={select}
      onKeyDown={(e) => {
        if (select && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          select();
        }
      }}
      hoverIndicator={checked || disabled ? undefined : 'background-hover'}
      gap="xsmall"
      style={{ opacity: disabled && !checked ? 0.6 : 1 }}
    >
      <Box direction="row" gap="small" align="center">
        {/* the theme's radio glyph (24px), drawn so the card stays the one control */}
        <Box
          round="full"
          width="24px"
          height="24px"
          border={{ color: checked ? 'border-selected' : 'border-strong', size: 'small' }}
          align="center"
          justify="center"
          flex={false}
          aria-hidden
        >
          {checked && <Box round="full" width="12px" height="12px" background="background-primary-strong" />}
        </Box>
        <Text weight={500} color="text-strong">
          {title}
        </Text>
      </Box>
      {children}
    </Box>
  );
}

/** The parts of a long step, done in order, the current one highlighted. */
export function PartsBar({ parts, at, doneAll, failed }: { parts: string[]; at: number; doneAll: boolean; failed?: boolean }) {
  return (
    <Box direction="row" align="center" gap="xsmall" wrap flex={false} role="list" aria-label="Parts of this step">
      {parts.map((p, i) => {
        const state: StepState =
          doneAll || i < at ? 'complete' : i === at ? (failed ? 'failed' : 'action_required') : 'not_started';
        return (
          <Box key={p} direction="row" align="center" gap="xsmall" role="listitem" aria-current={i === at && !doneAll ? 'step' : undefined}>
            {i > 0 && <Box pad={{ horizontal: 'small' }} border={{ side: 'top', color: i <= at ? 'border-strong' : 'border-weak' }} aria-hidden />}
            <Box
              direction="row"
              gap="xsmall"
              align="center"
              pad={{ horizontal: 'small', vertical: 'xsmall' }}
              round="large"
              background={i === at && !doneAll ? 'background-selected-primary' : undefined}
            >
              <StatusIcon state={state} />
              <Text size="small" weight={i === at ? 'bold' : 500} color={state === 'not_started' ? 'text-weak' : 'text-strong'}>
                {i + 1}. {p}
              </Text>
            </Box>
          </Box>
        );
      })}
    </Box>
  );
}
