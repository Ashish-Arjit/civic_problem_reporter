@echo off
echo Testing CivicFix Backend - Multi-Platform Edition
echo.

echo 1. Health Check
curl http://localhost:5050/health
echo.

echo 2. Simulated Social Login (Instagram)
curl -X POST -H "Content-Type: application/json" -d "{\"username\": \"CivicWarrior\", \"password\": \"secure123\", \"platform\": \"Instagram\"}" http://localhost:5050/simulate_social_login
echo.

echo 3. Submitting Complaint (with Instagram preference)
curl -X POST -F "username=DemoUser" -F "phone=9876543210" -F "latitude=12.9716" -F "longitude=77.5946" -F "priority=Critical" -F "preferred_platform=Instagram" http://localhost:5050/submit
echo.

echo 4. Forcing Escalation (Backdating by 50h)
curl -X POST http://localhost:5050/force_escalation
echo.

echo 5. Checking Pending (Instagram Simulation should pop up!)
curl http://localhost:5050/check_pending
echo.

echo 6. Mark Resolved
curl -X POST http://localhost:5050/mark_resolved/1
echo.

pause
