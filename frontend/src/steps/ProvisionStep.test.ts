import { describe, expect, it } from 'vitest';
import { RemovalItem } from '../api';
import { removalLines } from './ProvisionStep';

const item = (kind: string, name: string): RemovalItem => ({ kind, name, command: `remove${kind} -f ${name}` });

describe('removalLines', () => {
  it('orders the undo so it pastes top to bottom: schedules and exports before what they use', () => {
    const items = [
      item('host', 'h1'), item('volume', 'v1'), item('vlun', 'v1-h1'), item('hostset', 'hs1'),
      item('vvset', 'vs1'), item('snapshot', 's1'), item('schedule', 'sc1'),
    ];
    expect(removalLines(items).map((line) => line.split(' ')[0])).toEqual([
      'removeschedule', 'removesnapshot', 'removevlun', 'removevvset', 'removevolume', 'removehostset', 'removehost',
    ]);
  });

  it('keeps the order within a kind and puts an unknown kind last', () => {
    const items = [item('mystery', 'm1'), item('volume', 'b'), item('volume', 'a'), item('host', 'h1')];
    expect(removalLines(items)).toEqual(['removevolume -f b', 'removevolume -f a', 'removehost -f h1', 'removemystery -f m1']);
  });

  it('writes a command once when several applies removed the same object', () => {
    expect(removalLines([item('volume', 'v1'), item('host', 'h1'), item('volume', 'v1')])).toEqual(['removevolume -f v1', 'removehost -f h1']);
  });

  it('does not reorder the caller\u2019s list', () => {
    const items = [item('host', 'h1'), item('vlun', 'x')];
    removalLines(items);
    expect(items.map((i) => i.kind)).toEqual(['host', 'vlun']);
  });
});
