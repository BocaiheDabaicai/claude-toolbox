import { z } from 'zod'

export const emailSchema = z
  .string()
  .trim()
  .toLowerCase()
  .max(255, '邮箱过长')
  .regex(/^[^@\s]+@[^@\s]+\.[^@\s]+$/, '邮箱格式不正确')

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, '请输入密码').max(128, '密码过长'),
})

export type LoginInput = z.infer<typeof loginSchema>
