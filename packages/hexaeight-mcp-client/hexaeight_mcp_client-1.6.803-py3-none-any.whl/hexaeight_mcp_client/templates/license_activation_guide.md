# HexaEight License Activation Guide

## Quick Setup Process ⚡

### Step 1: Prepare Your Identity (2-4 minutes)
📱 **Download HexaEight Authenticator app** (iOS/Android)

**Choose your identity type:**
- 🎲 **Generic Resource** (2 min): Tap "Create Generic Resource" → get `storm23-cloud-wave-bright09`
- 🌐 **Domain Resource** (4 min): Use your domain → `weather-agent.yourcompany.com`

### Step 2: Purchase License 
🛒 **Visit**: https://store.hexaeight.com
- Select CPU count for your machine
- Minimum 5 days License
- Pricing: 1 CPU = $15, 2 CPU = $30, 4 CPU = $60

### Step 3: Activate License
```bash
./HexaEight-Machine-Tokens-Utility --newtoken
```

**Activation Flow:**
1. 🎯 Enter your resource name (generic or domain)
2. 📱 Open QR code link in browser
3. ⚡ Scan QR code with HexaEight app
4. 🔐 Approve identity assignment in mobile app
5. ⏎ Press Enter to complete activation

### Step 4: Verify Success
✅ Check for `hexaeight.mac` file in current directory

---

## License Renewal
```bash
./HexaEight-Machine-Tokens-Utility --renewtoken
```

## Next Steps After Activation
```bash
# Create organized workspace
hexaeight-start create-directory-linked-to-hexaeight-license my-ai-project

# Generate agent configurations
hexaeight-start generate-parent-or-child-agent-licenses

# Deploy sample system
hexaeight-start deploy-multi-ai-agent-samples
```

## Important Notes
- 📄 License file (`hexaeight.mac`) cannot be moved after creation
- 🔗 Use hardlinks to reference license from other directories
- ⚠️ Keep license file secure in its original location
- 🎯 License enables unlimited child agent creation during active period
- ♾️ Child agents work forever, even after license expires

## Support Resources
- 📖 Github : https://github.com/HexaEightTeam/hexaeight-mcp-client
- 🛒 License Store: https://store.hexaeight.com
- 📱 Mobile App: Search "HexaEight Authenticator"
