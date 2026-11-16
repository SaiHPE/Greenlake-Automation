import { Box, Button, Header, Menu, Nav, ResponsiveContext, Text } from 'grommet';
import { Apps, Close, LinkPrevious } from 'grommet-icons';
import { light } from 'hpe-design-tokens/grommet';
import { useContext } from 'react';
import { StatusIcon, StatusIndicator, StepState } from './status';

const BRAND = light.hpe.color.decorative.brand;

/**
 * The HPE Element. The Design System is explicit: "Always use the HPE Element at the top-left of
 * your service or product experience." Drawn here rather than taken from grommet-icons because that
 * icon still carries the previous brand green; this uses the decorative-brand token.
 *
 * The HPE GreenLake badge that used to sit here has been retired by the brand and removed.
 */
export function HpeElement({ width = 40 }: { width?: number }) {
  return (
    <svg width={width} height={width / 2} viewBox="0 0 48 24" role="img" aria-label="HPE" focusable="false">
      <path fillRule="evenodd" clipRule="evenodd" d="M2 6h44v12H2V6zm3 3h38v6H5V9z" fill={BRAND} />
    </svg>
  );
}

/**
 * The Design System app header: brand element and product name on the left, linking to the
 * landing page (Your runs); the open run and the Runs menu on the right.
 */
export function AppHeader({
  appName,
  serial,
  mode,
  runState,
  runLabel,
  onHome,
  onNewRun,
}: {
  appName: string;
  serial?: string;
  mode?: string;
  runState?: StepState;
  runLabel?: string;
  onHome: () => void;
  onNewRun: () => void;
}) {
  const size = useContext(ResponsiveContext);
  const narrow = size === 'small' || size === 'xsmall';
  return (
    <Header
      background="background-front"
      pad={{ horizontal: 'medium', vertical: 'small' }}
      border={{ side: 'bottom', color: 'border-weak' }}
      gap="medium"
      flex={false}
    >
      <Button plain onClick={onHome} a11yTitle={`HPE Alletra Storage MP ${appName}: your runs`}>
        <Box direction="row" align="center" gap="small">
          <HpeElement width={36} />
          <Box direction="row" gap="xsmall" align="baseline" wrap>
            <Text weight="bold" color="text-strong">
              HPE Alletra Storage MP
            </Text>
            <Text color="text-strong">{appName}</Text>
          </Box>
        </Box>
      </Button>
      <Box direction="row" align="center" gap="medium" flex={false}>
        {serial && !narrow && (
          <Box direction="row" align="center" gap="small">
            <Text size="small" weight="bold" color="text-strong">
              {serial}
            </Text>
            {mode && (
              <Text size="small" color="text-weak">
                {mode}
              </Text>
            )}
            {runState && <StatusIndicator state={runState} label={runLabel} />}
          </Box>
        )}
        <Menu
          label="Runs"
          items={[
            { label: 'Your runs', onClick: onHome },
            { label: 'Start a new run', onClick: onNewRun },
          ]}
          dropAlign={{ top: 'bottom', right: 'right' }}
        />
      </Box>
    </Header>
  );
}

/**
 * The Design System wizard header: the previous step by name on the left, what is being done in the
 * middle, Cancel on the right. A control that does not apply is not shown.
 */
export function WizardBar({
  flow,
  previous,
  cancel,
}: {
  flow: string;
  previous?: { label: string; onClick: () => void };
  cancel?: { label: string; onClick: () => void };
}) {
  const size = useContext(ResponsiveContext);
  const compact = size === 'small' || size === 'xsmall';
  return (
    <Header background="background-contrast" pad={{ horizontal: 'medium', vertical: 'xsmall' }} responsive={false} flex={false}>
      <Box direction="row" flex>
        {previous && (
          <Button
            icon={<LinkPrevious />}
            label={compact ? undefined : previous.label}
            a11yTitle={`Previous step: ${previous.label}`}
            onClick={previous.onClick}
          />
        )}
      </Box>
      <Text size="small" weight={500} color="text-strong" truncate>
        {flow}
      </Text>
      <Box direction="row" flex justify="end">
        {cancel && <Button icon={<Close />} label={compact ? undefined : cancel.label} reverse onClick={cancel.onClick} />}
      </Box>
    </Header>
  );
}

export interface RailItem {
  key: string;
  label: string;
  group: string;
  state: StepState;
  hint?: string;
  reachable: boolean;
}

function RailRow({
  label,
  hint,
  icon,
  current,
  reachable,
  a11yTitle,
  onSelect,
  muted,
}: {
  label: string;
  hint?: string;
  icon: React.ReactNode;
  current: boolean;
  reachable: boolean;
  a11yTitle: string;
  onSelect: () => void;
  muted?: boolean;
}) {
  return (
    <Box
      direction="row"
      gap="small"
      align="start"
      pad={{ horizontal: 'small', vertical: 'xsmall' }}
      round="xsmall"
      background={current ? 'background-selected-primary' : undefined}
      onClick={reachable ? onSelect : undefined}
      hoverIndicator={reachable && !current ? 'background-hover' : undefined}
      focusIndicator={reachable}
      flex={false}
      // Which step is active must be programmatic, not just bold text on a tinted row.
      role={reachable ? 'button' : undefined}
      aria-current={current ? 'step' : undefined}
      aria-disabled={reachable ? undefined : true}
      a11yTitle={a11yTitle}
      style={{ cursor: reachable ? 'pointer' : 'default' }}
    >
      <Box pad={{ top: 'xxsmall' }} flex={false}>
        {icon}
      </Box>
      <Box>
        <Text size="small" weight={current ? 'bold' : 500} color={muted && !current ? 'text-weak' : 'text-strong'}>
          {label}
        </Text>
        {hint && (
          <Text size="xsmall" color="text-weak">
            {hint}
          </Text>
        )}
      </Box>
    </Box>
  );
}

/**
 * The step rail, grouped by deployment stage.
 *
 * The Design System's wizard is linear and forward-only. This one is not: the operator chooses a
 * mode that selects a subset of steps, several steps wait on the operator, and any completed step
 * can be revisited. The rail is what makes that scope and position legible, so it stays, and the
 * step identifier carries "Step X of Y" to meet the progress guidance. See docs/UX-GUIDELINES.md.
 */
export function StepRail({
  items,
  activeKey,
  onSelect,
  overview,
  note,
}: {
  items: RailItem[];
  activeKey: string;
  onSelect: (key: string) => void;
  /** The run overview row, shown once a run exists. */
  overview?: { current: boolean; onSelect: () => void };
  note?: string;
}) {
  const size = useContext(ResponsiveContext);
  if (size === 'small' || size === 'xsmall') return null;
  const groups: { name: string; items: RailItem[] }[] = [];
  items.forEach((item) => {
    const existing = groups.find((group) => group.name === item.group);
    if (existing) existing.items.push(item);
    else groups.push({ name: item.group, items: [item] });
  });

  return (
    <Nav
      background="background-front"
      border={{ side: 'right', color: 'border-weak' }}
      pad={{ horizontal: 'xsmall', vertical: 'small' }}
      gap="small"
      width={{ min: 'small', max: 'medium' }}
      basis="1/6"
      flex={false}
      overflow="auto"
      a11yTitle="Steps of this run"
    >
      {overview && (
        <RailRow
          label="Run overview"
          hint="Every step on one page"
          icon={<Apps size="small" />}
          current={overview.current}
          reachable
          a11yTitle="Run overview"
          onSelect={overview.onSelect}
        />
      )}
      {groups.map((group) => (
        <Box key={group.name} gap="xxsmall" flex={false}>
          <Text size="small" weight={500} color="text-weak" margin={{ left: 'small', top: 'xsmall' }}>
            {group.name}
          </Text>
          {group.items.map((item) => (
            <RailRow
              key={item.key}
              label={item.label}
              hint={item.hint}
              icon={<StatusIcon state={item.state} />}
              current={item.key === activeKey}
              reachable={item.reachable}
              muted={item.state === 'not_started'}
              a11yTitle={`${item.label}: ${item.state.replace('_', ' ')}`}
              onSelect={() => onSelect(item.key)}
            />
          ))}
        </Box>
      ))}
      {note && (
        <Box pad="small" margin={{ top: 'xsmall' }} background="background-contrast" round="xsmall" flex={false}>
          <Text size="xsmall" color="text-weak">
            {note}
          </Text>
        </Box>
      )}
    </Nav>
  );
}
