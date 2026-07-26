import { Box, Button, Header, Nav, Text } from 'grommet';
import { FormPrevious } from 'grommet-icons';
import { light } from 'hpe-design-tokens/grommet';
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

/** Brand and service name on the left; which array, which mode and how the run is doing on the right. */
export function AppHeader({
  title,
  serial,
  mode,
  runState,
  runLabel,
}: {
  title: string;
  serial?: string;
  mode?: string;
  runState?: StepState;
  runLabel?: string;
}) {
  return (
    <Header
      background="background-front"
      pad={{ horizontal: 'medium', vertical: 'small' }}
      justify="between"
      align="center"
      gap="medium"
      flex={false}
    >
      <Box direction="row" align="center" gap="small" flex={false}>
        <HpeElement />
        <Text size="large" weight="bold" color="text-strong">
          {title}
        </Text>
      </Box>
      <Box direction="row" align="center" gap="small" flex={false} wrap>
        {serial && (
          <Text size="small" color="text-strong">
            {serial}
          </Text>
        )}
        {mode && (
          <>
            <Text size="small" color="text-weak">
              ·
            </Text>
            <Text size="small">{mode}</Text>
          </>
        )}
        {runState && (
          <>
            <Text size="small" color="text-weak">
              ·
            </Text>
            <StatusIndicator state={runState} label={runLabel} />
          </>
        )}
      </Box>
    </Header>
  );
}

/**
 * The wizard bar: Previous step on the left, Cancel run on the right, pinned above the step so both
 * stay reachable while scrolling — the Design System's wizard header controls.
 */
export function WizardBar({
  onPrevious,
  canGoPrevious,
  onCancel,
  canCancel,
}: {
  onPrevious: () => void;
  canGoPrevious: boolean;
  onCancel: () => void;
  canCancel: boolean;
}) {
  return (
    <Box
      direction="row"
      justify="between"
      align="center"
      pad={{ horizontal: 'medium', vertical: 'xsmall' }}
      border={{ side: 'bottom', color: 'border-weak' }}
      flex={false}
    >
      <Button icon={<FormPrevious />} label="Previous step" onClick={onPrevious} disabled={!canGoPrevious} />
      <Button label="Cancel run" onClick={onCancel} disabled={!canCancel} />
    </Box>
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

/**
 * The step rail, grouped by deployment stage.
 *
 * The Design System's wizard is linear and forward-only. This one is not: the operator chooses a
 * mode that selects a subset of steps, several steps wait on the operator, and any completed step
 * can be revisited. The rail is what makes that scope and position legible, so it stays — and the
 * step identifier carries "Step X of Y" to meet the progress guidance. See docs/UX-GUIDELINES.md.
 */
export function StepRail({
  items,
  activeKey,
  onSelect,
}: {
  items: RailItem[];
  activeKey: string;
  onSelect: (key: string) => void;
}) {
  const groups: { name: string; items: RailItem[] }[] = [];
  items.forEach((item) => {
    const existing = groups.find((group) => group.name === item.group);
    if (existing) existing.items.push(item);
    else groups.push({ name: item.group, items: [item] });
  });

  return (
    <Nav
      background="background-front"
      pad={{ horizontal: 'small', vertical: 'medium' }}
      gap="medium"
      width="medium"
      flex={false}
      overflow="auto"
      a11yTitle="Deployment steps"
    >
      {groups.map((group) => (
        <Box key={group.name} gap="xxsmall" flex={false}>
          <Text size="xsmall" weight={600} color="text-weak" margin={{ horizontal: 'small', bottom: 'xxsmall' }}>
            {group.name.toUpperCase()}
          </Text>
          {group.items.map((item) => {
            const current = item.key === activeKey;
            return (
              <Box
                key={item.key}
                direction="row"
                gap="small"
                align="center"
                pad={{ horizontal: 'small', vertical: 'xsmall' }}
                round="xsmall"
                background={current ? 'background-contrast' : undefined}
                onClick={item.reachable ? () => onSelect(item.key) : undefined}
                focusIndicator={item.reachable}
                flex={false}
                // Which step is active must be programmatic, not just bold text on a tinted row.
                role={item.reachable ? 'button' : undefined}
                aria-current={current ? 'step' : undefined}
                aria-disabled={item.reachable ? undefined : true}
                a11yTitle={`${item.label} — ${item.state.replace('_', ' ')}`}
                style={{ opacity: item.reachable ? 1 : 0.5, cursor: item.reachable ? 'pointer' : 'default' }}
              >
                <StatusIcon state={item.state} />
                <Box flex>
                  <Text size="small" weight={current ? 'bold' : undefined} color={current ? 'text-strong' : undefined}>
                    {item.label}
                  </Text>
                  {item.hint && (
                    <Text size="xsmall" color="text-weak">
                      {item.hint}
                    </Text>
                  )}
                </Box>
              </Box>
            );
          })}
        </Box>
      ))}
    </Nav>
  );
}
