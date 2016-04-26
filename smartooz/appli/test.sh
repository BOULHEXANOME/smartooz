flask --app=smartooz initdb

flask --app=smartooz run & 

sleep 2

echo "Register.. Expect OK"
curl -X POST -d '{"password":"hugo","username":"papin2","email":"balec"}' http://127.0.0.1:5000/register --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Register..  Expect err"
curl -X POST -d '{"password":"sdlvknxknv","username":"papin2","email":"balec2"}' http://127.0.0.1:5000/register --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Login.. Expect OK"
curl -X POST -d '{"password":"hugo","username":"papin2"}' http://127.0.0.1:5000/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add place1.. Expect OK"
curl -X POST -d '{"latitude":45.75,"longitude":4.8,"address":"ta mere","openning_hours":"tout le temps","name":"tour papine","description":"flemme","keywords":["sfm", "HOHO"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add place1 again.. Expect err"
curl -X POST -d '{"latitude":45.75,"longitude":4.8,"address":"ta mere","openning_hours":"tout le temps","name":"tour papine","description":"flemme","keywords":["sfm", "HOHO"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add place2.. Expect OK"
curl -X POST -d '{"latitude":45.76,"longitude":4.8,"address":"ta 2","openning_hours":"tout le temps","name":"tour sdk","description":"flemme","keywords":["sfm", "c est génial"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET all places.. Expect OK"
curl http://127.0.0.1:5000/get-places --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET places by keywords.. Expect OK"
curl "http://127.0.0.1:5000/get-places-keyword/?keywords=sfm&keywords=c%20est%20g%C3%A9nial" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET place1 by id.. (lat 45.75) Expect OK"
curl "http://127.0.0.1:5000/get-place-id/1" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET place1 by lat/long.. Expect OK"
curl "http://127.0.0.1:5000/get-place-coord/45.76,4.8" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "UPDATE place1.. Expect OK"
curl "http://127.0.0.1:5000/update-place" -X POST -d '{"id":1,"latitude":45.75,"longitude":4.8,"address":"ta 2","openning_hours":"tout le temps","name":"tour sdk","description":"flemme","keywords":["2e keyword", "c est génial"]}' --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET place1 by id.. (lat 45.75) Expect OK"
curl "http://127.0.0.1:5000/get-place-id/1" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Logout.. Expect OK -> updated"
curl http://127.0.0.1:5000/logout --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add place.. Expect err"
curl -X POST -d '{"latitude":45.77,"longitude":4.81,"address":"ta 2","openning_hours":"tout le temps","name":"tour sdk","description":"flemme","keywords":["sfm", "c est génial"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Login.. Expect OK"
curl -X POST -d '{"password":"hugo","username":"papin2"}' http://127.0.0.1:5000/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Delete user.. Expect OK"
curl -X POST http://127.0.0.1:5000/delete-user --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Login.. Expect err"
curl -X POST -d '{"password":"hugo","username":"papin2"}' http://127.0.0.1:5000/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
ps aux | grep python