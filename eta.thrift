/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements. See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership. The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License. You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

namespace py eta
namespace php eta

typedef i32 int;
typedef i64 int64;

struct Duration {
    1: int hours;
    2: int minutes;
    3: int seconds;
}

struct Range {
    1: Duration shortest;
    2: Duration longest;
}



struct Params {
    1: int area_id;
    2: int brand_id;
    3: int user_id;
    4: optional map<string,string> extra_data;
    5: optional list<string> extra_keys;
    6: optional bool test_mode;
}



struct Prediction {
    1: int area_id;
    2: int tasker_id;
    3: Range result;
    4: optional map<string,string> features;
}



exception InvalidInput {
    1: int error_code;
    2: string error_message;
}

exception ModelMissing {
    1: int error_code;
    2: string error_message;
}

struct Request_params{
    1: int area_id;
    2: map<string,string> contain;
}

struct Data {
    1: double result;
    2: map<string,string> extra_data; // 该值可容纳其他需求值
    3: optional map<string,string> features;
}

struct PredictionResult {
    1: string request_id; // sys.maxsize-timeshamp
    2: int error;
    3: optional string err_msg;
    4: list<Data> data;
}

service EstimateTaskDurations {
    string listKeys();
    bool clearCache();
    string clearCacheByKey(1: string cache_key);    //cache_key可以逗号分隔
    string reloadPickleCache(1: string cache_key);  //cache_key可以逗号分隔

    PredictionResult predictTime(1: list<Params> queries)

}