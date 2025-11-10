Param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [switch]$SeedReset,
  [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red }

function Invoke-Api {
  Param(
    [ValidateSet('GET','POST','PUT','PATCH','DELETE')] [string]$Method,
    [string]$Url,
    [hashtable]$Body = $null,
    [hashtable]$Headers = $null
  )
  try {
    $params = @{ Uri = $Url; Method = $Method }
    if ($Headers) { $params.Headers = $Headers }
    if ($Body) {
      $json = $Body | ConvertTo-Json -Depth 6
      $params.ContentType = 'application/json'
      $params.Body = $json
      if ($Verbose) { Write-Info "POST/PUT/PATCH body: $json" }
    }
    $resp = Invoke-RestMethod @params
    return @{ success = $true; data = $resp }
  } catch {
    $statusCode = $null
    $content = $null
    try { $statusCode = $_.Exception.Response.StatusCode.value__ } catch {}
    try {
      $sr = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
      $content = $sr.ReadToEnd(); $sr.Close()
    } catch {}
    return @{ success = $false; status = $statusCode; error = $content }
  }
}

Write-Info "BaseUrl = $BaseUrl"

if ($SeedReset) {
  Write-Info "Reset + seed de usuarios"
  python "scripts/seed_users.py" --reset | Out-Host
}

# Health check
$health = Invoke-Api -Method GET -Url "$BaseUrl/health"
if (-not $health.success) { Write-Fail "Health check: $($health.status) $($health.error)"; exit 1 }
Write-Ok "Health: $($health.data | ConvertTo-Json -Depth 3)"

# Login por email (admin)
$loginAdmin = Invoke-Api -Method POST -Url "$BaseUrl/api/v1/login" -Body @{ email = 'admin@example.com'; password = 'admin123' }
if (-not $loginAdmin.success) { Write-Fail "Login admin (email): $($loginAdmin.status) $($loginAdmin.error)"; exit 1 }
$tokenAdmin = $loginAdmin.data.access_token
Write-Ok "Login admin (email) OK"

# Login por nombre (alias en campo 'email')
$loginByName = Invoke-Api -Method POST -Url "$BaseUrl/api/v1/login" -Body @{ email = 'Admin'; password = 'admin123' }
if (-not $loginByName.success) { Write-Fail "Login admin (nombre): $($loginByName.status) $($loginByName.error)" } else { Write-Ok "Login admin (nombre) OK" }

$authAdmin = @{ Authorization = "Bearer $tokenAdmin" }

# Profile (JWT)
$profile = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/profile" -Headers $authAdmin
if (-not $profile.success) { Write-Fail "Profile: $($profile.status) $($profile.error)"; exit 1 }
Write-Ok "Profile: $($profile.data | ConvertTo-Json -Depth 3)"
$adminId = $profile.data.user_id
# Opcional: perfil completo vía /profiles/me
$profileMe = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/profiles/me" -Headers $authAdmin
if ($profileMe.success) { Write-Ok "Profiles/me OK" } else { Write-Info "Profiles/me no disponible: $($profileMe.status)" }

# Admin area (role admin)
$adminArea = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/admin" -Headers $authAdmin
if (-not $adminArea.success) { Write-Fail "Admin area: $($adminArea.status) $($adminArea.error)"; exit 1 }
Write-Ok "Admin area OK"

# Users: create (admin-only), list, get, update, delete
$newUserPayload = @{ name = 'Test User'; email = 'test.user@example.com'; password = 'test123'; role = 'user' }
$createUser = Invoke-Api -Method POST -Url "$BaseUrl/api/v1/users/" -Body $newUserPayload -Headers $authAdmin
if (-not $createUser.success) { Write-Fail "Create user: $($createUser.status) $($createUser.error)"; exit 1 }
$userId = $createUser.data.id
Write-Ok "Create user id=$userId"

$listUsers = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/users/" -Headers $authAdmin
if (-not $listUsers.success) { Write-Fail "List users: $($listUsers.status) $($listUsers.error)"; exit 1 }
Write-Ok "List users count=$($listUsers.data.Count)"

$getUser = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/users/$userId" -Headers $authAdmin
if (-not $getUser.success) { Write-Fail "Get user: $($getUser.status) $($getUser.error)"; exit 1 }
Write-Ok "Get user OK"

$updateUserPayload = @{ name = 'Test User Updated' }
$updateUser = Invoke-Api -Method PUT -Url "$BaseUrl/api/v1/users/$userId" -Body $updateUserPayload -Headers $authAdmin
if (-not $updateUser.success) { Write-Fail "Update user: $($updateUser.status) $($updateUser.error)"; exit 1 }
Write-Ok "Update user OK"

# Users: PATCH (parcial)
$patchUserPayload = @{ role = 'user'; name = 'Test User Patched' }
$patchUser = Invoke-Api -Method PATCH -Url "$BaseUrl/api/v1/users/$userId" -Body $patchUserPayload -Headers $authAdmin
if (-not $patchUser.success) { Write-Fail "Patch user: $($patchUser.status) $($patchUser.error)"; exit 1 }
Write-Ok "Patch user OK"

$deleteUser = Invoke-Api -Method DELETE -Url "$BaseUrl/api/v1/users/$userId" -Headers $authAdmin
if (-not $deleteUser.success) { Write-Fail "Delete user: $($deleteUser.status) $($deleteUser.error)"; exit 1 }
Write-Ok "Delete user OK"

# Categories: create, list, get, update
$cat1Payload = @{ name = 'Libros'; description = 'Material de lectura' }
$cat2Payload = @{ name = 'Novela'; description = 'Narrativa' }
$createCat1 = Invoke-Api -Method POST -Url "$BaseUrl/api/v1/categories/" -Body $cat1Payload -Headers $authAdmin
if (-not $createCat1.success) { Write-Fail "Create category Libros: $($createCat1.status) $($createCat1.error)"; exit 1 }
$cat1Id = $createCat1.data.id
Write-Ok "Create category 'Libros' id=$cat1Id"

$createCat2 = Invoke-Api -Method POST -Url "$BaseUrl/api/v1/categories/" -Body $cat2Payload -Headers $authAdmin
if (-not $createCat2.success) { Write-Fail "Create category Novela: $($createCat2.status) $($createCat2.error)"; exit 1 }
$cat2Id = $createCat2.data.id
Write-Ok "Create category 'Novela' id=$cat2Id"

$listCats = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/categories/" -Headers $authAdmin
if (-not $listCats.success) { Write-Fail "List categories: $($listCats.status) $($listCats.error)"; exit 1 }
Write-Ok "List categories count=$($listCats.data.Count)"

$getCat1 = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/categories/$cat1Id" -Headers $authAdmin
if (-not $getCat1.success) { Write-Fail "Get category Libros: $($getCat1.status) $($getCat1.error)"; exit 1 }
Write-Ok "Get category Libros OK"

$updateCat2Payload = @{ description = 'Narrativa actualizada' }
$updateCat2 = Invoke-Api -Method PUT -Url "$BaseUrl/api/v1/categories/$cat2Id" -Body $updateCat2Payload -Headers $authAdmin
if (-not $updateCat2.success) { Write-Fail "Update category Novela: $($updateCat2.status) $($updateCat2.error)"; exit 1 }
Write-Ok "Update category Novela OK"

# Items: create (admin/user), list, get, update, patch, delete
$newItemPayload = @{ title = 'Sample Item'; description = 'Created by script'; owner_id = [int]$adminId; category_ids = @([int]$cat1Id) }
$createItem = Invoke-Api -Method POST -Url "$BaseUrl/api/v1/items/" -Body $newItemPayload -Headers $authAdmin
if (-not $createItem.success) { Write-Fail "Create item: $($createItem.status) $($createItem.error)"; exit 1 }
$itemId = $createItem.data.id
Write-Ok "Create item id=$itemId"

$listItems = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/items/" -Headers $authAdmin
if (-not $listItems.success) { Write-Fail "List items: $($listItems.status) $($listItems.error)"; exit 1 }
Write-Ok "List items count=$($listItems.data.Count)"

$getItem = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/items/$itemId" -Headers $authAdmin
if (-not $getItem.success) { Write-Fail "Get item: $($getItem.status) $($getItem.error)"; exit 1 }
Write-Ok "Get item OK"

$updateItemPayload = @{ title = 'Sample Item Updated' }
$updateItem = Invoke-Api -Method PUT -Url "$BaseUrl/api/v1/items/$itemId" -Body $updateItemPayload -Headers $authAdmin
if (-not $updateItem.success) { Write-Fail "Update item: $($updateItem.status) $($updateItem.error)"; exit 1 }
Write-Ok "Update item OK"

# Items: PATCH (parcial, incluyendo categorías)
$patchItemPayload = @{ description = 'Patched by script'; category_ids = @([int]$cat1Id, [int]$cat2Id) }
$patchItem = Invoke-Api -Method PATCH -Url "$BaseUrl/api/v1/items/$itemId" -Body $patchItemPayload -Headers $authAdmin
if (-not $patchItem.success) { Write-Fail "Patch item: $($patchItem.status) $($patchItem.error)"; exit 1 }
Write-Ok "Patch item OK"

# Items: filtro por categoría (cat2)
$itemsByCat2 = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/items/?category_id=$cat2Id" -Headers $authAdmin
if ($itemsByCat2.success) { Write-Ok "Filter items by category Novela OK (count=$($itemsByCat2.data.Count))" } else { Write-Fail "Filter items by category: $($itemsByCat2.status) $($itemsByCat2.error)" }

$deleteItem = Invoke-Api -Method DELETE -Url "$BaseUrl/api/v1/items/$itemId" -Headers $authAdmin
if (-not $deleteItem.success) { Write-Fail "Delete item: $($deleteItem.status) $($deleteItem.error)"; exit 1 }
Write-Ok "Delete item OK"

# Categories: delete
$deleteCat1 = Invoke-Api -Method DELETE -Url "$BaseUrl/api/v1/categories/$cat1Id" -Headers $authAdmin
if (-not $deleteCat1.success) { Write-Fail "Delete category Libros: $($deleteCat1.status) $($deleteCat1.error)" } else { Write-Ok "Delete category Libros OK" }
$deleteCat2 = Invoke-Api -Method DELETE -Url "$BaseUrl/api/v1/categories/$cat2Id" -Headers $authAdmin
if (-not $deleteCat2.success) { Write-Fail "Delete category Novela: $($deleteCat2.status) $($deleteCat2.error)" } else { Write-Ok "Delete category Novela OK" }

# Guest token: prueba acceso restringido
$loginGuest = Invoke-Api -Method POST -Url "$BaseUrl/api/v1/login" -Body @{ email = 'guest1@example.com'; password = 'guest123' }
if (-not $loginGuest.success) { Write-Fail "Login guest: $($loginGuest.status) $($loginGuest.error)" } else {
  $tokenGuest = $loginGuest.data.access_token
  $authGuest = @{ Authorization = "Bearer $tokenGuest" }
  $guestItems = Invoke-Api -Method GET -Url "$BaseUrl/api/v1/items/" -Headers $authGuest
  if ($guestItems.success) { Write-Ok "Guest GET items OK" } else { Write-Fail "Guest GET items: $($guestItems.status) $($guestItems.error)" }
  $guestCreateItem = Invoke-Api -Method POST -Url "$BaseUrl/api/v1/items/" -Body @{ title='Guest Item'; description='Should be forbidden'; owner_id=[int]$adminId } -Headers $authGuest
  if (-not $guestCreateItem.success -and $guestCreateItem.status -eq 403) { Write-Ok "Guest POST items correctly forbidden (403)" } else { Write-Fail "Guest POST items expected 403, got: $($guestCreateItem | ConvertTo-Json -Depth 5)" }
}

Write-Host ""; Write-Ok "Todas las pruebas de autenticación y operaciones han finalizado"