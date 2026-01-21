#!/usr/bin/env python3
import dbus
import dbus.mainloop.glib
import dbus.service
import requests
from gi.repository import GLib

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
NEXT_TURN_UUID = "12345678-1234-5678-1234-56789abcdef1"
CURRENT_PLAYER_UUID = "12345678-1234-5678-1234-56789abcdef2"


API_URL = "http://127.0.0.1:8000/api/advance_turn"


# ---------- BLE Base Classes ----------

class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = "/org/bluez/dnd"
        self.services = []
        super().__init__(bus, self.path)

    def get_path(self):
        return self.path

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            for chrc in service.characteristics:
                response[chrc.get_path()] = chrc.get_properties()
        return response


class Service(dbus.service.Object):
    def __init__(self, bus, index, uuid):
        self.path = f"/org/bluez/example/service{index}"
        self.bus = bus
        self.uuid = uuid
        self.characteristics = []
        super().__init__(bus, self.path)

    def get_path(self):
        return self.path

    def add_characteristic(self, chrc):
        self.characteristics.append(chrc)

    def get_properties(self):
        return {
            "org.bluez.GattService1": {
                "UUID": self.uuid,
                "Primary": True,
            }
        }


class Characteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = f"{service.get_path()}/char{index}"
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.service = service
        super().__init__(bus, self.path)

    def get_path(self):
        return self.path

    def get_properties(self):
        return {
            "org.bluez.GattCharacteristic1": {
                "UUID": self.uuid,
                "Service": self.service.get_path(),
                "Flags": self.flags,
            }
        }

    @dbus.service.method(
        "org.bluez.GattCharacteristic1",
        in_signature="aya{sv}",
        out_signature=""
    )
    def WriteValue(self, value, options):
        pass


# ---------- Your Next Turn Characteristic ----------

class CurrentPlayerCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        super().__init__(
            bus,
            index,
            CURRENT_PLAYER_UUID,
            ["read", "notify"],  # allow reading and notifications
            service,
        )
        self.value = "0,0,Unknown,0"
        self.subscribed_devices = []

    @dbus.service.method(
        "org.bluez.GattCharacteristic1",
        in_signature="", out_signature="ay"
    )
    def ReadValue(self):
        return [dbus.Byte(c.encode("utf-8")) for c in self.value]

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature="", out_signature="")
    def StartNotify(self):
        print("Notifications started")
        # You could track subscribed devices if needed

    @dbus.service.method(
        "org.bluez.GattCharacteristic1",
        in_signature="", out_signature=""
    )
    def StopNotify(self):
        print("Notifications stopped")

    # Call this after next/previous turn to update app
    def update(self, encounter_id, combatant_count, player_name, player_hp):
        self.value = f"{encounter_id},{combatant_count},{player_name},{player_hp}"
        # Send notification to all subscribed devices
        # (optional: you can implement real notifications)


class NextTurnCharacteristic(Characteristic):
    def __init__(self, bus, index, service, current_player_chrc):
        super().__init__(bus, index, NEXT_TURN_UUID, ["write"], service)
        self.current_player_chrc = current_player_chrc

    @dbus.service.method(
        "org.bluez.GattCharacteristic1",
        in_signature="aya{sv}", out_signature=""
    )
    def WriteValue(self, value, options):
        decoded = bytes(value).decode("utf-8")
        print("BLE NextTurn received:", decoded)

        try:
            encounter_id, combatant_count = decoded.split(",")

            r = requests.post(
                API_URL,
                data={
                    "encounter_id": encounter_id,
                    "combatant_count": combatant_count,
                },
                timeout=2,
            )

            if r.ok:
                print("Turn advanced successfully")
                # Use the returned JSON to update the current player characteristic
                data = r.json()
                player_name = data.get("active_player_name", "Unknown")
                player_hp = data.get("active_player_hp", "0")

                # Update CurrentPlayerCharacteristic including encounter_id & combatant_count
                self.current_player_chrc.update(encounter_id, combatant_count, player_name, player_hp)
            else:
                print("API error:", r.text)



        except Exception as e:
            print("BLE handling error:", e)


# ---------- Advertisement ----------

class Advertisement(dbus.service.Object):
    PATH_BASE = "/org/bluez/example/advertisement"

    def __init__(self, bus, index):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.service_uuids = [SERVICE_UUID]
        super().__init__(bus, self.path)

    def get_path(self):
        return self.path

    @dbus.service.method("org.bluez.LEAdvertisement1", out_signature="")
    def Release(self):
        print("Advertisement released")

    @dbus.service.method(
        "org.freedesktop.DBus.Properties",
        in_signature="ss",
        out_signature="v",
    )
    def Get(self, interface, prop):
        if prop == "ServiceUUIDs":
            return dbus.Array(self.service_uuids, signature="s")
        raise dbus.exceptions.DBusException("Invalid property")

    @dbus.service.method(
        "org.freedesktop.DBus.Properties",
        in_signature="s",
        out_signature="a{sv}",
    )
    def GetAll(self, interface):
        return {
            "Type": "peripheral",
            "ServiceUUIDs": dbus.Array(self.service_uuids, signature="s"),
            "LocalName": "DnD-Encounter",
        }


# ---------- Main ----------

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    app = Application(bus)    

    service = Service(bus, 0, SERVICE_UUID)
    
    current_player_chrc = CurrentPlayerCharacteristic(bus, 0, service)
    next_turn_chrc = NextTurnCharacteristic(bus, 1, service, current_player_chrc)

    service.add_characteristic(current_player_chrc)
    service.add_characteristic(next_turn_chrc)

    app.add_service(service)

    ad = Advertisement(bus, 0)

    adapter = "/org/bluez/hci0"

    service_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter),
        GATT_MANAGER_IFACE,
    )

    service_manager.RegisterApplication(
        app.get_path(), {},
        reply_handler=lambda: print("GATT registered"),
        error_handler=lambda e: print("GATT error:", e),
    )

    ad_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter),
        LE_ADVERTISING_MANAGER_IFACE,
    )

    ad_manager.RegisterAdvertisement(
        ad.get_path(), {},
        reply_handler=lambda: print("Advertising"),
        error_handler=lambda e: print("Advertise error:", e),
    )

    print("BLE server entering main loop")
    GLib.MainLoop().run()



if __name__ == "__main__":
    main()
