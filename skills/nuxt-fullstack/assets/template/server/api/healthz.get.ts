export default defineEventHandler(() => ({
  status: 'ok',
  service: '__PROJECT_NAME__',
  time: new Date().toISOString(),
}))
