export type UserRole = 'admin' | 'operator'

export const USER_ROLE_LABELS: Record<UserRole, string> = {
  admin: '管理员',
  operator: '运营',
}

export interface SessionUser {
  id: number
  email: string
  name: string
  role: UserRole
}
