export type UserRole = 'admin' | 'operator'

export interface SessionUser {
  id: number
  email: string
  name: string
  role: UserRole
}
