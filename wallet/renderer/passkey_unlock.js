/**
 * PayQuant (PQN) WebAuthn / Passkey Biometric Unlock Module v4.0.0
 * Provides native biometric security (TouchID, FaceID, Windows Hello, YubiKey) for wallet access.
 */
const PasskeyUnlock = {
  isAvailable() {
    return window.PublicKeyCredential !== undefined && typeof window.PublicKeyCredential === 'function';
  },

  async registerPasskey(userAddress) {
    if (!this.isAvailable()) {
      throw new Error("Biometric Passkey API is not supported on this browser/device.");
    }

    const challenge = new Uint8Array(32);
    window.crypto.getRandomValues(challenge);

    const userId = new TextEncoder().encode(userAddress || "pqn_wallet_user");

    const publicKeyCredentialCreationOptions = {
      challenge: challenge,
      rp: {
        name: "PayQuant Light Wallet",
        id: window.location.hostname || "localhost",
      },
      user: {
        id: userId,
        name: userAddress || "user@payquant.network",
        displayName: "PayQuant Wallet User",
      },
      pubKeyCredParams: [{ alg: -7, type: "public-key" }],
      authenticatorSelection: {
        authenticatorAttachment: "platform",
        userVerification: "preferred"
      },
      timeout: 60000,
      attestation: "direct"
    };

    try {
      const credential = await navigator.credentials.create({
        publicKey: publicKeyCredentialCreationOptions
      });
      if (credential) {
        localStorage.setItem('pqn-passkey-id', credential.id);
        return { success: true, credentialId: credential.id };
      }
    } catch (e) {
      console.warn("Biometric Passkey registration skipped:", e);
      return { success: false, error: e.message };
    }
  },

  async authenticatePasskey() {
    if (!this.isAvailable()) {
      return { success: false, error: "Passkeys not supported" };
    }
    const credId = localStorage.getItem('pqn-passkey-id');
    const challenge = new Uint8Array(32);
    window.crypto.getRandomValues(challenge);

    const allowCredentials = credId ? [{
      id: Uint8Array.from(atob(credId), c => c.charCodeAt(0)),
      type: 'public-key'
    }] : [];

    try {
      const assertion = await navigator.credentials.get({
        publicKey: {
          challenge: challenge,
          allowCredentials: allowCredentials,
          userVerification: "preferred"
        }
      });
      if (assertion) {
        return { success: true };
      }
    } catch (e) {
      console.warn("Passkey authentication fallback to PIN:", e);
      return { success: false, error: e.message };
    }
  }
};

if (typeof window !== 'undefined') {
  window.PasskeyUnlock = PasskeyUnlock;
}
