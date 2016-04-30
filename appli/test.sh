flask --app=smartooz initdb

HOST=127.0.0.1 # 142.4.215.20
PORT=5001

echo "Register.. Expect OK"
curl -X POST -d '{"password":"hugo","username":"papin2","email":"balec"}' http://$HOST:$PORT/register --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Register..  Expect err"
curl -X POST -d '{"password":"sdlvknxknv","username":"papin2","email":"balec2"}' http://$HOST:$PORT/register --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Login.. Expect OK"
curl -X POST -d '{"password":"hugo","username":"papin2"}' http://$HOST:$PORT/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add place1.. Expect OK"
curl -X POST -d '{"latitude":45.75,"longitude":4.8,"address":"ta mere","phone":"0602050809","website":"www.truc.fr","openning_hours":"tout le temps","name":"tour papine","description":"flemme","keywords":["sfm", "HOHO"]}' http://$HOST:$PORT/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add place1 again.. Expect err"
curl -X POST -d '{"latitude":45.75,"longitude":4.8,"address":"ta mere","phone":"0602050809","website":"www.truc.fr","openning_hours":"tout le temps","name":"tour papine","description":"flemme","keywords":["sfm", "HOHO"]}' http://$HOST:$PORT/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add place2.. Expect OK"
curl -X POST -d '{"latitude":45.76,"longitude":4.8,"address":"ta 2","phone":"0602050809","website":"www.truc.fr","openning_hours":"tout le temps","name":"tour sdk","description":"flemme","keywords":["sfm", "c est génial"]}' http://$HOST:$PORT/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET all places.. Expect OK"
curl http://$HOST:$PORT/get-places --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET places by keywords.. Expect OK"
curl "http://$HOST:$PORT/get-places-keyword?keywords=sfm&keywords=c%20est%20g%C3%A9nial" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET place1 by id.. (lat 45.75) Expect OK"
curl "http://$HOST:$PORT/get-place-id/1" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET place1 by lat/long.. Expect OK"
curl "http://$HOST:$PORT/get-place-coord/45.75,4.8" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET places by coord radius.. (lat 45.75, long 4.8, radius 20) Expect OK"
curl "http://$HOST:$PORT/get-place-radius-coord/45.75,4.8,5" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "UPDATE place1.. Expect OK"
curl "http://$HOST:$PORT/update-place" -X POST -d '{"id":1,"latitude":45.75,"longitude":4.8,"address":"ta 2","openning_hours":"tout le temps","name":"tour sdk","description":"flemme","keywords":["2e keyword", "c est génial"]}' --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Vote place.. Expect OK"
curl -X POST -d '{"id":1, "note": 4.5}' http://$HOST:$PORT/vote-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET place1 by id.. (lat 45.75) Expect OK"
curl "http://$HOST:$PORT/get-place-id/1" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add circuit.. Expect OK"
curl -X POST -d '{"name":"mon circuit","description":"ma description","keywords":["keyWord-circuit", "2eKeyW"],"places":[1,2]}' http://$HOST:$PORT/add-circuit --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET circuit by id.. Expect OK"
curl "http://$HOST:$PORT/get-circuit-id/1" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Edit circuit.. Expect OK"
curl -X POST -d '{"id":1, "name":"mon circuit","description":"ma 2","keywords":["keyWord-circuit", "2aaaa"],"places":[1]}' http://$HOST:$PORT/update-circuit --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Vote circuit.. Expect OK"
curl -X POST -d '{"id":1, "note": 5}' http://$HOST:$PORT/vote-circuit --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET circuit by id.. Expect OK"
curl "http://$HOST:$PORT/get-circuit-id/1" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Set circuit done by user.. Expect OK"
curl -X POST -d '{"id":1}' "http://$HOST:$PORT/circuit-done" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET circuits done.. Expect OK"
curl "http://$HOST:$PORT/get-id-circuits-done" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "upload.. Expect OK"
curl -X POST -F "image=@./test_upload.jpg" "http://$HOST:$PORT/upload/1,1" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "upload.. Expect OK"
curl -X POST -F "image=@./test_upload.jpg" "http://$HOST:$PORT/upload/1,2" -c /tmp/cookie -b /tmp/cookie


rm -f ./test_download_ok.jpg
echo
echo
echo "download.. Expect OK"
curl -X GET "http://$HOST:$PORT/download-picture/1,1" -c /tmp/cookie -b /tmp/cookie > ./test_download_ok.jpg

echo
echo
echo "GET circuits by keyword.. Expect OK"
curl "http://$HOST:$PORT/get-circuits-keyword?keywords=keyWord-circuit&keywords=2aaaa" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Logout.. Expect OK"
curl "http://$HOST:$PORT/logout" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Add place.. Expect err"
curl -X POST -d '{"latitude":45.77,"longitude":4.81,"address":"ta 2","openning_hours":"tout le temps","name":"tour sdk","description":"flemme","keywords":["sfm", "c est génial"]}' http://$HOST:$PORT/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Login.. Expect OK"
curl -X POST -d '{"password":"hugo","username":"papin2"}' http://$HOST:$PORT/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET keywords of places.. Expect OK"
curl "http://$HOST:$PORT/get-all-places-keywords" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET keywords of circuits.. Expect OK"
curl "http://$HOST:$PORT/get-all-circuits-keywords" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET all circuits.. Expect OK"
curl "http://$HOST:$PORT/get-circuits" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "DELETE circuit.. Expect OK"
curl "http://$HOST:$PORT/delete-circuit" -X POST -d '{"circuit_id":1}' --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "DELETE place.. Expect OK"
curl "http://$HOST:$PORT/delete-place" -X POST -d '{"place_id":1}' --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET place1 by id.. (lat 45.75) Expect ERROR"
curl "http://$HOST:$PORT/get-place-id/1" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "GET circuit by id.. Expect ERROR"
curl "http://$HOST:$PORT/get-circuit-id/1" --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Delete user.. Expect OK"
curl -X POST http://$HOST:$PORT/delete-user --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo
echo
echo "Login.. Expect err"
curl -X POST -d '{"password":"hugo","username":"papin2"}' http://$HOST:$PORT/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo