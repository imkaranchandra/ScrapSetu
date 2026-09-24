import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    print("🧪 Starting ScrapSetu API Test Suite...\n")
    client = TestClient(app)

    # 1. Root Health Check
    res = client.get("/")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("✅ Health check passed:", res.json())

    # 2. Scrap Rates
    res = client.get("/api/rates")
    assert res.status_code == 200
    rates = res.json()
    assert len(rates) >= 7, "Default rates not properly seeded"
    print(f"✅ Scrap rates loaded successfully ({len(rates)} materials):")
    for r in rates[:3]:
        print(f"   - {r['material']}: {r['currency']}{r['rate_per_kg']}/{r['unit']}")

    # 3. Rates Dictionary
    res = client.get("/api/rates/dict")
    assert res.status_code == 200
    rates_dict = res.json()
    assert "Plastic" in rates_dict and rates_dict["Plastic"] == 20.0
    print("✅ Rates dictionary lookup passed:", rates_dict)

    # 4. Collector Auth Registration
    collector_payload = {
        "mobile": "9811122233",
        "password": "password123",
        "full_name": "Aman Sharma",
        "role": "collector",
        "address": "Shop 12, Market Road",
        "city": "Mumbai"
    }
    # Clear existing if any by unique test mobile
    res = client.post("/api/auth/register", json=collector_payload)
    if res.status_code == 400: # Already exists
        res = client.post("/api/auth/login", json={"mobile": "9811122233", "password": "password123"})
    assert res.status_code in [200, 201], f"Collector auth failed: {res.text}"
    collector_data = res.json()
    collector_token = collector_data["access_token"]
    collector_headers = {"Authorization": f"Bearer {collector_token}"}
    print("✅ Collector registered/logged in:", collector_data["user"]["full_name"])

    # 5. Recycler Auth Registration
    recycler_payload = {
        "mobile": "9988776655",
        "password": "password123",
        "full_name": "Rajesh Patel",
        "role": "recycler",
        "business_name": "EcoClean Recycling Pvt Ltd",
        "address": "Industrial Area Phase 2",
        "city": "Mumbai"
    }
    res = client.post("/api/auth/register", json=recycler_payload)
    if res.status_code == 400:
        res = client.post("/api/auth/login", json={"mobile": "9988776655", "password": "password123"})
    assert res.status_code in [200, 201], f"Recycler auth failed: {res.text}"
    recycler_data = res.json()
    recycler_token = recycler_data["access_token"]
    recycler_headers = {"Authorization": f"Bearer {recycler_token}"}
    print("✅ Recycler registered/logged in:", recycler_data["user"]["full_name"], f"({recycler_data['user']['business_name']})")

    # 6. Current User Profile (/me)
    res = client.get("/api/auth/me", headers=collector_headers)
    assert res.status_code == 200
    assert res.json()["mobile"] == "9811122233"
    print("✅ /api/auth/me profile verification passed")

    # 7. Submit Scrap Lot (Collector)
    scrap_payload = {
        "material": "Copper",
        "weight": 5.0,
        "pickup_address": "Shop 12, Market Road, Mumbai",
        "collector_notes": "High grade copper wiring"
    }
    res = client.post("/api/scrap", json=scrap_payload, headers=collector_headers)
    assert res.status_code == 201, f"Failed to submit scrap: {res.text}"
    created_lot = res.json()
    lot_id = created_lot["id"]
    assert created_lot["status"] == "Pending"
    assert created_lot["price"] == 3000.0  # 600 * 5
    print(f"✅ Scrap lot created: #{created_lot['lot_number']} - {created_lot['material']} ({created_lot['weight']}kg) = ₹{created_lot['price']}")

    # 8. Collector Collections History
    res = client.get("/api/scrap/my-collections", headers=collector_headers)
    assert res.status_code == 200
    collections = res.json()
    assert any(c["id"] == lot_id for c in collections)
    print(f"✅ Collector collections retrieved ({len(collections)} items)")

    # 9. Recycler Views Incoming Lots
    res = client.get("/api/scrap/incoming", headers=recycler_headers)
    assert res.status_code == 200
    incoming = res.json()
    assert any(c["id"] == lot_id for c in incoming)
    print(f"✅ Recycler incoming lots retrieved ({len(incoming)} pending items)")

    # 10. Recycler Accepts Lot
    res = client.post(f"/api/scrap/{lot_id}/accept", headers=recycler_headers)
    assert res.status_code == 200, f"Accept lot failed: {res.text}"
    accepted_lot = res.json()
    assert accepted_lot["status"] == "Accepted"
    print(f"✅ Recycler accepted lot {lot_id}. Status: {accepted_lot['status']}")

    # 11. Logistics / Active Pickup
    res = client.get("/api/pickups/active", headers=recycler_headers)
    assert res.status_code == 200
    active_pickup = res.json()
    assert active_pickup is not None and active_pickup["id"] == lot_id
    print(f"✅ Active pickup verified for Lot #{active_pickup['lot_number']}. Driver: {active_pickup['pickup']['driver_name']}")

    # 12. Recycler Confirms Handover (Completion)
    res = client.post(f"/api/scrap/{lot_id}/handover", headers=recycler_headers)
    assert res.status_code == 200, f"Handover failed: {res.text}"
    completed_lot = res.json()
    assert completed_lot["status"] == "Completed"
    print(f"✅ Scrap handover confirmed. Final Status: {completed_lot['status']}")

    # 13. Recycler Transaction History
    res = client.get("/api/scrap/history", headers=recycler_headers)
    assert res.status_code == 200
    history = res.json()
    assert any(c["id"] == lot_id for c in history)
    print(f"✅ Transaction history verified ({len(history)} accepted/completed lots)")

    # 14. Dashboard Analytics & Stats
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    stats = res.json()
    print("✅ Dashboard stats verified:")
    print(f"   - Total Lots: {stats['total_lots']}")
    print(f"   - Completed Lots: {stats['completed_lots']}")
    print(f"   - Total Weight: {stats['total_weight_kg']} kg")
    print(f"   - Total Scrap Value: ₹{stats['total_value_rs']}")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! The ScrapSetu backend is fully functional!")

if __name__ == "__main__":
    run_tests()
