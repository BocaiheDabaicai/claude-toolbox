export type CustomerStatus = 'active' | 'inactive'

export interface Customer {
  id: number
  name: string
  phone: string | null
  email: string | null
  company: string | null
  note: string | null
  status: CustomerStatus
  createdAt: string
  updatedAt: string
  deletedAt: string | null
}

export interface CustomerList {
  rows: Customer[]
  total: number
  page: number
  pageSize: number
}
