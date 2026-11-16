import { Box, Button, Text } from 'grommet';
import { useEffect, useState } from 'react';
import { ArrayCredentialInfo, CredentialOverride, getRun } from '../api';
import { Section } from './blocks';
import { CredentialsFields } from './primitives';

/**
 * ADR 0013 / SPEC-008 R4 — the array credential card shared by Verify and As-built.
 *
 * The run holds one array credential from the sheet (Provisioning tab, else the DSCC system
 * credential). When it does, the card says so in one line and offers "Use a different credential";
 * only when the run holds none does the form show by default. The old "never stored" help text is
 * gone: it promised what the run had already given up two steps earlier.
 */
export function useArrayCredential(runId: string) {
  const [info, setInfo] = useState<ArrayCredentialInfo | null | undefined>(undefined);
  useEffect(() => {
    let live = true;
    getRun(runId)
      .then((detail) => { if (live) setInfo(detail.array_credential ?? null); })
      .catch(() => { if (live) setInfo(null); });
    return () => { live = false; };
  }, [runId]);
  return info; // undefined = loading, null = unknown/unavailable
}

const SOURCE_LABEL: Record<ArrayCredentialInfo['source'], string> = {
  provisioning: "the sheet's Provisioning tab",
  dscc_setup: "the sheet's DSCC system credential",
  none: 'nowhere',
};

export function ArrayCredentialCard({
  info,
  serial,
  override,
  onOverride,
}: {
  info: ArrayCredentialInfo | null | undefined;
  serial?: string;
  override: CredentialOverride;
  onOverride: (value: CredentialOverride) => void;
}) {
  const held = !!info?.available;
  const [editing, setEditing] = useState(false);
  const showForm = !held || editing;
  const username = override?.username ?? '3paradm';
  const password = override?.password ?? '';
  const set = (u: string, p: string) => onOverride({ username: u, password: p });

  return (
    // remounts once the run's credential is known, so it opens by itself when the run holds none
    <Section
      key={info === undefined ? 'loading' : held ? 'held' : 'none'}
      title="Array credentials"
      open={info !== undefined && !held}
      summary={
        held
          ? override
            ? `Using a different credential for this step: ${override.username || 'no user name yet'}`
            : `From ${SOURCE_LABEL[info!.source]}: ${info!.username} @ ${info!.host || serial || 'this array'} · held by this run only`
          : info === undefined
            ? 'Reading the run'
            : `None held by this run. Enter the array admin account for ${serial ?? 'this array'}.`
      }
    >
      {held && !editing && (
        <Box direction="row" align="center" gap="small" wrap>
          <Text size="small" color="text-weak">Typed once, on the sheet. A different credential here is used for this step only and is not stored.</Text>
          <Button size="small" label="Use a different credential" onClick={() => setEditing(true)} />
        </Box>
      )}
      {showForm && (
        <Box gap="xsmall">
          <CredentialsFields
            username={username}
            password={password}
            onUsername={(u) => set(u, password)}
            onPassword={(p) => set(username, p)}
            help={
              held
                ? 'Overrides the sheet credential for this step only.'
                : 'The run has no array credential; this one is used for this step only and is not stored.'
            }
          />
          {held && editing && (
            <Box direction="row">
              <Button size="small" label="Back to the sheet credential" onClick={() => { setEditing(false); onOverride(null); }} />
            </Box>
          )}
        </Box>
      )}
    </Section>
  );
}

/** True when the step's action may run: the run holds a credential, or the operator typed a full pair. */
export function credentialReady(info: ArrayCredentialInfo | null | undefined, override: CredentialOverride): boolean {
  if (override) return !!override.username.trim() && !!override.password;
  return !!info?.available;
}
