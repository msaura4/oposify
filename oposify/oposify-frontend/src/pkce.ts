import pkceChallenge from 'pkce-challenge';

export async function getPKCE() {
    const result = await pkceChallenge();
    const { code_verifier, code_challenge } = result;
    
    console.log('PKCE generated - code_verifier:', code_verifier);
    console.log('PKCE generated - code_challenge:', code_challenge);
    
    localStorage.setItem('pkce_code_verifier', code_verifier);
    
    // Verify it was stored
    const stored = localStorage.getItem('pkce_code_verifier');
    console.log('PKCE stored in localStorage:', stored);
    console.log('PKCE stored matches generated:', stored === code_verifier);
    
    return code_challenge;
}