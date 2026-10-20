# Checks catalog

Expiry sources and how the scan reads them. Some are management plane and covered by Reader; some are data plane or directory reads that need their own permission and are best effort. Where a read is denied, record the source as not assessed and continue.

For each finding the tool records: item name, kind, source, subscription, expiry date, days remaining, a severity from the days remaining, and the recommended action.

## 1. App Service certificates (Resource Graph, Reader)

```
az graph query -q "resources | where type =~ 'microsoft.web/certificates' | project name, id, subscriptionId, resourceGroup, expirationDate=tostring(properties.expirationDate), thumbprint=tostring(properties.thumbprint)" --first 1000
```

The expirationDate is management plane metadata, so this works with Reader. Fix for a finding: renew or replace the certificate and update the binding.

## 2. Key Vault certificates and secrets (data plane)

List the vaults, then read item expiry from each vault's data plane.

```
az graph query -q "resources | where type =~ 'microsoft.keyvault/vaults' | project name, id, subscriptionId, resourceGroup, vaultUri=tostring(properties.vaultUri)" --first 1000
```

The tool reads {vaultUri}certificates and {vaultUri}secrets with a token for the https://vault.azure.net audience and takes the attributes.exp value. This needs a Key Vault read permission (Key Vault Reader plus a data action, or a list access policy). A vault that denies the read is recorded as not assessed. Managed secrets that back a certificate are skipped to avoid double counting. Fix for a finding: rotate the secret, or renew the certificate (enable autorotation where the issuer supports it).

Verify one vault by hand:

```
az keyvault certificate list --vault-name <vault> --query "[].{name:name, expires:attributes.expires}"
az keyvault secret list --vault-name <vault> --query "[?attributes.expires].{name:name, expires:attributes.expires}"
```

## 3. Application and service principal credentials (Microsoft Graph)

```
GET https://graph.microsoft.com/v1.0/applications?$select=displayName,appId,passwordCredentials,keyCredentials
```

The tool reads passwordCredentials and keyCredentials endDateTime with a token for the Microsoft Graph audience. This needs a directory read (for example Application.Read.All). Where it is not granted, the source is recorded as not assessed. Fix for a finding: roll the client secret or certificate credential before it expires and update the consumers.

## Severity from days remaining

- Critical: already expired (days remaining below zero).
- High: 14 days or fewer.
- Medium: 15 to 30 days.
- Low: 31 days to the horizon (60 by default).

Beyond the horizon: not reported. Pass a larger horizon argument for more lead time before a big renewal season.

## Note on App Gateway and other embedded certificates

Certificates embedded directly in an Application Gateway or a Front Door listener are not enumerated here; prefer Key Vault referenced certificates, which this skill can see. Where embedded certificates are in use, check them by hand and consider moving them to Key Vault.
