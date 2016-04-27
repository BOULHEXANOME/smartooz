flask --app=smartooz initdb

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
curl -X POST -d '{"latitude":45.75,"longitude":4.8,"address":"ta mere","phone":"0602050809","website":"www.truc.fr","openning_hours":"tout le temps","name":"tour papine","description":"flemme","keywords":["sfm", "HOHO"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add place1 again.. Expect err"
curl -X POST -d '{"latitude":45.75,"longitude":4.8,"address":"ta mere","phone":"0602050809","website":"www.truc.fr","openning_hours":"tout le temps","name":"tour papine","description":"flemme","keywords":["sfm", "HOHO"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add place2.. Expect OK"
curl -X POST -d '{"latitude":45.76,"longitude":4.8,"address":"ta 2","phone":"0602050809","website":"www.truc.fr","openning_hours":"tout le temps","name":"tour sdk","description":"flemme","keywords":["sfm", "c est génial"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

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
curl "http://127.0.0.1:5000/get-place-coord/45.75,4.8" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET places by coord radius.. (lat 45.75, long 4.8, radius 20) Expect OK"
curl "http://127.0.0.1:5000/get-place-radius-coord/45.75,4.8,5" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

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
echo "Add circuit.. Expect OK"
curl -X POST -d '{"name":"mon circuit","description":"ma description","keywords":["keyWord-circuit", "2eKeyW"],"places":[1,2]}' http://127.0.0.1:5000/add-circuit --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET circuit by id.. Expect OK"
curl "http://127.0.0.1:5000/get-circuit-id/1" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Edit circuit.. Expect OK"
curl -X POST -d '{"id":1, "name":"mon circuit","description":"ma 2","keywords":["keyWord-circuit", "2aaaa"],"places":[1]}' http://127.0.0.1:5000/update-circuit --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET circuit by id.. Expect OK"
curl "http://127.0.0.1:5000/get-circuit-id/1" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET circuits by keyword.. Expect OK"
curl "http://127.0.0.1:5000/get-circuits-keyword/?keywords=keyWord-circuit&keywords=2aaaa" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Logout.. Expect OK"
curl "http://127.0.0.1:5000/logout" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

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
echo "GET keywords of places.. Expect OK"
curl "http://127.0.0.1:5000/get-all-places-keywords" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET keywords of circuits.. Expect OK"
curl "http://127.0.0.1:5000/get-all-circuits-keywords" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET all circuits.. Expect OK"
curl "http://127.0.0.1:5000/get-circuits" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Delete user.. Expect OK"
curl -X POST http://127.0.0.1:5000/delete-user --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Login.. Expect err"
curl -X POST -d '{"password":"hugo","username":"papin2"}' http://127.0.0.1:5000/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo