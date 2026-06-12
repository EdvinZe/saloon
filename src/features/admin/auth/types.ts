export interface AdminAuthState {
  authenticated: boolean
  role: string | null
  username: string | null
}

export interface AdminLoginPayload {
  username: string
  password: string
}
