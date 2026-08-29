const tokenStorageKey = 'lia2AdminToken'

export class AdminSessionService {
  getToken(): string {
    return window.sessionStorage.getItem(tokenStorageKey) ?? ''
  }

  setToken(token: string): void {
    window.sessionStorage.setItem(tokenStorageKey, token)
  }

  clearToken(): void {
    window.sessionStorage.removeItem(tokenStorageKey)
  }

  isAuthenticated(): boolean {
    return this.getToken().length > 0
  }
}
