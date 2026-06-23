import customtkinter as ctk
import threading
import requests
from theme import COLORS, FONTS
from ui.console import Console

class AzureToolsPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        lbl = ctk.CTkLabel(self, text="Azure AD & Intune Cloud Sync", font=FONTS["title"], text_color=COLORS["accent_blue"])
        lbl.pack(pady=10)

        auth_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"])
        auth_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(auth_frame, text="Tenant ID:", font=FONTS["small"]).grid(row=0, column=0, padx=10, pady=5)
        self.tenant = ctk.CTkEntry(auth_frame, width=200, placeholder_text="0000-0000-0000-0000")
        self.tenant.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(auth_frame, text="Client ID:", font=FONTS["small"]).grid(row=0, column=2, padx=10, pady=5)
        self.client_id = ctk.CTkEntry(auth_frame, width=200, placeholder_text="App Registration ID")
        self.client_id.grid(row=0, column=3, padx=10, pady=5)

        ctk.CTkLabel(auth_frame, text="Secret:", font=FONTS["small"]).grid(row=1, column=0, padx=10, pady=5)
        self.secret = ctk.CTkEntry(auth_frame, width=200, placeholder_text="Client Secret", show="*")
        self.secret.grid(row=1, column=1, padx=10, pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(btn_frame, text="Fetch Entra ID Users", command=lambda: self.run_graph("users")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Fetch Intune Devices", command=lambda: self.run_graph("devices")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Check Auth Token", fg_color=COLORS["accent_green"], command=lambda: self.run_graph("auth")).pack(side="left", padx=10)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, padx=10, pady=10)
        self.console.write("Azure AD (Entra) & Microsoft Intune Graph API Interfacer.")
        self.console.write("Requires an Azure App Registration with User.Read.All and DeviceManagementManagedDevices.Read.All permissions.")

    def run_graph(self, action):
        tenant = self.tenant.get()
        cid = self.client_id.get()
        sec = self.secret.get()
        
        if not tenant or not cid or not sec:
            self.console.write("\n❌ Error: Missing Azure App Registration Credentials (Tenant, Client ID, Secret).")
            return

        self.console.write(f"\n> Contacting Microsoft Graph API [{action}]...")
        
        def task():
            try:
                import msal
                app = msal.ConfidentialClientApplication(cid, authority=f"https://login.microsoftonline.com/{tenant}", client_credential=sec)
                result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
                
                if "access_token" in result:
                    token = result["access_token"]
                    headers = {'Authorization': f'Bearer {token}'}
                    
                    if action == "auth":
                        self.console.write("✅ Authentication Successful. Bearer Token acquired.")
                    elif action == "users":
                        graph_data = requests.get('https://graph.microsoft.com/v1.0/users?$top=10', headers=headers).json()
                        self.console.write(f"✅ Fetched Entra ID Users:\n{graph_data}")
                    elif action == "devices":
                        graph_data = requests.get('https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?$top=10', headers=headers).json()
                        self.console.write(f"✅ Fetched Intune Devices:\n{graph_data}")
                else:
                    self.console.write(f"❌ Auth Failed: {result.get('error_description', 'Unknown error')}")
            except ImportError:
                self.console.write("❌ Error: MSAL library is not installed.")
            except Exception as e:
                self.console.write(f"❌ Exception during Graph API Call: {e}")

        threading.Thread(target=task, daemon=True).start()
