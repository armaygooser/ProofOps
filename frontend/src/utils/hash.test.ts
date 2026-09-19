import { describe, expect, it } from 'vitest';

import { shortHash } from './hash';

describe('shortHash', () => {
  it('keeps both identity-bearing ends of a SHA-256 digest', () => {
    expect(shortHash('1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'))
      .toBe('12345678…abcdef');
  });

  it('marks a missing digest explicitly', () => {
    expect(shortHash(null)).toBe('—');
  });
});
