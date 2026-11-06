import { Box, Text } from 'grommet';
import { ReactNode } from 'react';

/**
 * An ordered list of operator instructions.
 *
 * The rest of this module — Section, StatusTag, EventIcon, EventLog — has been replaced by ui/:
 * Surface, StatusIndicator and ActivityTimeline, so that status and layout have one definition
 * each rather than one per screen.
 */
export function Instructions({ items }: { items: ReactNode[] }) {
  return (
    <Box as="ol" margin={{ vertical: 'none', left: 'small' }} pad={{ left: 'medium' }} gap="xsmall" flex={false}>
      {items.map((item, index) => (
        <Text as="li" size="small" key={index}>
          {item}
        </Text>
      ))}
    </Box>
  );
}
