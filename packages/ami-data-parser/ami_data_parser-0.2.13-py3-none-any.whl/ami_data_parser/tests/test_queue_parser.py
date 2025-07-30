from unittest import TestCase
from ami_data_parser.parser.queue_parser import QueueParser


class QueueParserTestCase(TestCase):

    def test_get_data(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        expect_data = [{'members': [{'name': 'SIP/IP-100-CdFaT', 'has_paused': True, 'reason_paused': None, 'dynamic':None, 'in_call': False, 'paused_time': 2930362, 'logged_time': 2930362, 'total_calls': 0, 'penalty': 0,'last_call_time': 0}, {'name': 'SIP/IP-101', 'has_paused': False, 'reason_paused': None, 'dynamic':None, 'in_call': False, 'paused_time': 0, 'logged_time': 2930362, 'total_calls': 0, 'penalty': 0,'last_call_time': 0}], 'waiting_calls': [], 'queuename': 'Queue_11', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0}, {'members': [], 'waiting_calls': [], 'queuename': 'Queue_27', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0}, {'members': [{'name': 'SIP/IP-100-boazN', 'has_paused': False, 'paused_time': 0, 'reason_paused': None, 'dynamic':None, 'in_call': False, 'logged_time': 2930362, 'total_calls': 0, 'penalty': 0,'last_call_time': 0}, {'name': 'SIP/IP-101-Iathq', 'has_paused': False, 'reason_paused': None, 'dynamic':None, 'in_call': False, 'paused_time': 0, 'logged_time': 2930362, 'total_calls': 0, 'penalty': 0,'last_call_time': 0}], 'waiting_calls': [], 'queuename': 'Queue_44', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0}, {'members': [], 'waiting_calls': [], 'queuename': 'Queue_47', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0}]
        queue_parser = QueueParser()
        data = queue_parser.get_data(received_data)
        self.assertListEqual(data, expect_data)
    
    def test_get_data_without_queue(self):
        received_data = ['Response: Success\r\n', 'ActionID: tatianno-ThinkPad-L470-00000003\r\n', 'Message: Command output follows\r\n', 'Output: No queues.\r\n']
        expect_data = []
        queue_parser = QueueParser()
        data = queue_parser.get_data(received_data)
        self.assertListEqual(data, expect_data)
        
    def test_get_list_queue_lines(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        expect_data = [["Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n'], ["Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n'], ["Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n'], ["Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']]
        queue_parser = QueueParser()
        data = queue_parser._get_list_queue_lines(received_data)
        self.assertListEqual(data, expect_data)
    
    def test_get_list_queue_lines_without_output_word(self):
        received_data = ['Response: Follows\r\n', 'Privilege: Command\r\n', 'ActionID: pbx-jhf-00000029\r\n', "Queue_110 has 6 calls (max unlimited) in 'rrmemory' strategy (45s holdtime, 310s talktime), W:0, C:124, A:242, SL:0.0% within 0s\n", '   Members: \n', '      Agent_428 (SIP/105-IPCZncL) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken no calls yet\n', '      Agent_309 (SIP/319-IPOrtLZ) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', '      Agent_461 (SIP/137-IPM87rR) (ringinuse disabled) (dynamic) (in call) (In use) has taken 19 calls (last was 108 secs ago)\n', '      Agent_308 (SIP/318-IPFJ95b) (ringinuse disabled) (dynamic) (Invalid) has taken no calls yet\n', '      Agent_460 (SIP/136-IP8IaBB) (ringinuse disabled) (dynamic) (in call) (In use) has taken 14 calls (last was 496 secs ago)\n', '      Agent_351 (SIP/350-IP4DdD2) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', '      Agent_307 (SIP/317-IPCtTYh) (ringinuse disabled) (dynamic) (Unavailable) has taken no calls yet\n', '      Agent_210 (SIP/292-IP8Gzzl) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', '      Agent_459 (SIP/134-IPF8nR3) (ringinuse disabled) (dynamic) (in call) (In use) has taken 28 calls (last was 191 secs ago)\n', '      Agent_458 (SIP/133-IPXaZiz) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken 32 calls (last was 302 secs ago)\n', '      Agent_304 (SIP/314-IPgfPCZ) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', '      Agent_457 (SIP/132-IPAo8gE) (ringinuse disabled) (dynamic) (Not in use) has taken 13 calls (last was 579 secs ago)\n', '      Agent_303 (SIP/313-IPtgY79) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', '      Agent_413 (SIP/397) (ringinuse disabled) (dynamic) (Not in use) has taken 3 calls (last was 11076 secs ago)\n', '      Agent_302 (SIP/312-IPuZ3n7) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken no calls yet\n', '      Agent_227 (SIP/IP-130-flz8s) (ringinuse disabled) (dynamic) (Invalid) has taken no calls yet\n', '      Agent_292 (SIP/IP-192-qYMin) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', '      Agent_438 (SIP/377-IPOmZ0a) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken no calls yet\n', '      Agent_275 (SIP/285-IPtVeO2) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', '      Agent_264 (SIP/284-IPr3v3A) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', '      Agent_287 (SIP/308-IPBA0xb) (ringinuse disabled) (dynamic) (paused) (In use) has taken no calls yet\n', '      Agent_445 (SIP/126-IPC0Vmd) (ringinuse disabled) (dynamic) (Not in use) has taken 7 calls (last was 8732 secs ago)\n', '      Agent_442 (SIP/374-IPn9TAY) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', '      Agent_498 (SIP/159-IPnfLhM) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken no calls yet\n', '      Agent_380 (SIP/373-IPzE0Ma) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', '      Agent_336 (SIP/339-IP9O9Z2) (ringinuse disabled) (dynamic) (Unavailable) has taken no calls yet\n', '      Agent_338 (SIP/338-IPi5tbT) (ringinuse disabled) (dynamic) (Unavailable) has taken no calls yet\n', '      Agent_339 (SIP/336-IPDqFeB) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken no calls yet\n', '      Agent_479 (SIP/154-IPr39Zr) (ringinuse disabled) (dynamic) (Unavailable) has taken no calls yet\n', '      Agent_225 (SIP/278-IPezbZg) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', '      Agent_224 (SIP/277-IPrjQBQ) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', '      Agent_223 (SIP/276-IPeLQQD) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', '      Agent_415 (SIP/398-IP62Ton) (ringinuse disabled) (dynamic) (Invalid) has taken no calls yet\n', '      Agent_411 (SIP/396-IPEiN9R) (ringinuse disabled) (dynamic) (Not in use) has taken 5 calls (last was 10702 secs ago)\n', '      Agent_422 (SIP/110-IPzfCjJ) (ringinuse disabled) (dynamic) (Unavailable) has taken no calls yet\n', '      Agent_216 (SIP/268-IPsfacv) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', '      Agent_213 (SIP/265-IPoxH5b) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken 3 calls (last was 2667 secs ago)\n', '   Callers: \n', '      1. SIP/551120872200-000864df (wait: 2:30, prio: 0)\n', '      2. SIP/5435204040-00086508 (wait: 1:27, prio: 0)\n', '      3. SIP/551120872200-00086527 (wait: 1:15, prio: 0)\n', '      4. SIP/551120872200-0008654a (wait: 0:40, prio: 0)\n', '      5. SIP/551120872200-0008659c (wait: 0:06, prio: 0)\n', '      6. SIP/551120872200-00086596 (wait: 0:01, prio: 0)\n', '\n', "Queue_435 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0% within 0s\n", '   Members: \n', '      SIP/388-IPoGO3b (ringinuse disabled) (In use) has taken no calls yet\n', '      SIP/403-IPuNdIC (ringinuse disabled) (Unavailable) has taken no calls yet\n', '      SIP/379-IPL8D33 (ringinuse disabled) (In use) has taken no calls yet\n', '      SIP/287-IPcdhrw (ringinuse disabled) (Unavailable) has taken no calls yet\n', '      SIP/114-IPgrNRH (ringinuse disabled) (Not in use) has taken no calls yet\n', '      SIP/359-IPcdAiX (ringinuse disabled) (Not in use) has taken no calls yet\n', '   No Callers\n', '\n', "Queue_500 has 0 calls (max unlimited) in 'ringall' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0% within 0s\n", '   Members: \n', '      SIP/105-IPCZncL (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/138-IPtB4BJ (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/374-IPn9TAY (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/125-IPgxdHC (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/157-IPGO4DP (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/213-IPZHgJN (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/338-IPi5tbT (ringinuse disabled) (Unavailable) has taken no calls yet\n', '      SIP/337-IPtmIFp (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/210-IPu1jOw (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/335-IPvOHVb (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/369-IPlFqAZ (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/399-IPlgNTQ (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/238-IP4Qase (ringinuse disabled) (Unavailable) has taken no calls yet\n', '      SIP/111-IP4RT8z (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '   No Callers\n', '\n', "Queue_501 has 0 calls (max unlimited) in 'ringall' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0% within 0s\n", '   Members: \n', '      SIP/263-IP2i5Zq (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/387-IPZ5ZXM (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/283-IPg9X51 (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/271-IP4eb3Q (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/269-IPEGdZ0 (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/392-IPl4lZH (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '   No Callers\n', '\n', "Queue_291 has 11 calls (max unlimited) in 'random' strategy (676s holdtime, 880s talktime), W:0, C:29, A:141, SL:0.0% within 0s\n", '   Members: \n', '      SIP/105-IPCZncL (ringinuse disabled) (paused) (Not in use) has taken 6 calls (last was 2309 secs ago)\n', '      SIP/263-IP2i5Zq (ringinuse disabled) (paused) (Unavailable) has taken 5 calls (last was 1735 secs ago)\n', '      SIP/138-IPtB4BJ (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/387-IPZ5ZXM (ringinuse disabled) (paused) (Not in use) has taken 3 calls (last was 6559 secs ago)\n', '      Agent_397 (SIP/383-IPc23wN) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', '      SIP/374-IPn9TAY (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/125-IPgxdHC (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/283-IPg9X51 (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/157-IPGO4DP (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/213-IPZHgJN (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/338-IPi5tbT (ringinuse disabled) (Unavailable) has taken no calls yet\n', '      SIP/337-IPtmIFp (ringinuse disabled) (paused) (Not in use) has taken 3 calls (last was 7342 secs ago)\n', '      SIP/210-IPu1jOw (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/335-IPvOHVb (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/369-IPlFqAZ (ringinuse disabled) (paused) (Unavailable) has taken 1 calls (last was 14701 secs ago)\n', '      Agent_375 (SIP/368-IPDZewZ) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', '      SIP/366-IPqqHwa (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '      SIP/399-IPlgNTQ (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/238-IP4Qase (ringinuse disabled) (Unavailable) has taken no calls yet\n', '      SIP/271-IP4eb3Q (ringinuse disabled) (paused) (Not in use) has taken 1 calls (last was 7955 secs ago)\n', '      SIP/111-IP4RT8z (ringinuse disabled) (paused) (Not in use) has taken 8 calls (last was 6339 secs ago)\n', '      SIP/269-IPEGdZ0 (ringinuse disabled) (paused) (Not in use) has taken 2 calls (last was 2844 secs ago)\n', '      SIP/392-IPl4lZH (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '   Callers: \n', '      1. SIP/551120872200-00085b93 (wait: 27:45, prio: 0)\n', '      2. SIP/551120872200-00085cc2 (wait: 24:01, prio: 0)\n', '      3. SIP/551120872200-00085e58 (wait: 18:11, prio: 0)\n', '      4. SIP/551120872200-0008605e (wait: 13:25, prio: 0)\n', '      5. SIP/551120872200-000860c8 (wait: 12:27, prio: 0)\n', '      6. SIP/551120872200-00086210 (wait: 7:47, prio: 0)\n', '      7. SIP/551120872200-000862ff (wait: 4:47, prio: 0)\n', '      8. SIP/551120872200-000862e1 (wait: 4:45, prio: 0)\n', '      9. SIP/551120872200-000862ed (wait: 4:42, prio: 0)\n', '      10. SIP/551120872200-00086344 (wait: 3:41, prio: 0)\n', '      11. SIP/551120872200-0008633a (wait: 3:41, prio: 0)\n', '\n', "Queue_238 has 2 calls (max unlimited) in 'ringall' strategy (104s holdtime, 717s talktime), W:0, C:28, A:19, SL:0.0% within 0s\n", '   Members: \n', '      SIP/262-IPJM3GO (ringinuse disabled) (paused) (Busy) has taken no calls yet\n', '      SIP/385-IPTivIr (ringinuse disabled) (paused) (Not in use) has taken 13 calls (last was 2544 secs ago)\n', '      SIP/315-IPw00cr (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      Agent_304 (SIP/314-IPgfPCZ) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', '      Agent_240 (SIP/IP-137-VN8Ff) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', '      SIP/IP-176-Jf1ll (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/IP-189-JQQsD (ringinuse disabled) (paused) (Not in use) has taken 1 calls (last was 9920 secs ago)\n', '      SIP/IP-188-R33In (ringinuse disabled) (paused) (In use) has taken no calls yet\n', '      SIP/308-IPBA0xb (ringinuse disabled) (paused) (In use) has taken no calls yet\n', '      SIP/281-IPgV576 (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/280-IP0pOQg (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/279-IPP7Qqg (ringinuse disabled) (paused) (Not in use) has taken 12 calls (last was 995 secs ago)\n', '      SIP/394-IPDoQmZ (ringinuse disabled) (In use) has taken no calls yet\n', '      SIP/391-IPcrVn0 (ringinuse disabled) (Not in use) has taken 2 calls (last was 11668 secs ago)\n', '   Callers: \n', '      1. SIP/20872200-0008644e (wait: 4:51, prio: 0)\n', '      2. SIP/20872200-00086572 (wait: 0:55, prio: 0)\n', '\n', "Queue_365 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0% within 0s\n", '   Members: \n', '      SIP/353-IP2f1fL (ringinuse disabled) (Unavailable) has taken no calls yet\n', '      SIP/374-IPn9TAY (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', '      SIP/366-IPqqHwa (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', '   No Callers\n', '\n', '--END COMMAND--\r\n']
        expected_data = [["Output:    Queue_110 has 6 calls (max unlimited) in 'rrmemory' strategy (45s holdtime, 310s talktime), W:0, C:124, A:242, SL:0.0% within 0s\n", 'Output:       Members: \n', 'Output:          Agent_428 (SIP/105-IPCZncL) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken no calls yet\n', 'Output:          Agent_309 (SIP/319-IPOrtLZ) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', 'Output:          Agent_461 (SIP/137-IPM87rR) (ringinuse disabled) (dynamic) (in call) (In use) has taken 19 calls (last was 108 secs ago)\n', 'Output:          Agent_308 (SIP/318-IPFJ95b) (ringinuse disabled) (dynamic) (Invalid) has taken no calls yet\n', 'Output:          Agent_460 (SIP/136-IP8IaBB) (ringinuse disabled) (dynamic) (in call) (In use) has taken 14 calls (last was 496 secs ago)\n', 'Output:          Agent_351 (SIP/350-IP4DdD2) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', 'Output:          Agent_307 (SIP/317-IPCtTYh) (ringinuse disabled) (dynamic) (Unavailable) has taken no calls yet\n', 'Output:          Agent_210 (SIP/292-IP8Gzzl) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', 'Output:          Agent_459 (SIP/134-IPF8nR3) (ringinuse disabled) (dynamic) (in call) (In use) has taken 28 calls (last was 191 secs ago)\n', 'Output:          Agent_458 (SIP/133-IPXaZiz) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken 32 calls (last was 302 secs ago)\n', 'Output:          Agent_304 (SIP/314-IPgfPCZ) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', 'Output:          Agent_457 (SIP/132-IPAo8gE) (ringinuse disabled) (dynamic) (Not in use) has taken 13 calls (last was 579 secs ago)\n', 'Output:          Agent_303 (SIP/313-IPtgY79) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', 'Output:          Agent_413 (SIP/397) (ringinuse disabled) (dynamic) (Not in use) has taken 3 calls (last was 11076 secs ago)\n', 'Output:          Agent_302 (SIP/312-IPuZ3n7) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken no calls yet\n', 'Output:          Agent_227 (SIP/IP-130-flz8s) (ringinuse disabled) (dynamic) (Invalid) has taken no calls yet\n', 'Output:          Agent_292 (SIP/IP-192-qYMin) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', 'Output:          Agent_438 (SIP/377-IPOmZ0a) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken no calls yet\n', 'Output:          Agent_275 (SIP/285-IPtVeO2) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', 'Output:          Agent_264 (SIP/284-IPr3v3A) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', 'Output:          Agent_287 (SIP/308-IPBA0xb) (ringinuse disabled) (dynamic) (paused) (In use) has taken no calls yet\n', 'Output:          Agent_445 (SIP/126-IPC0Vmd) (ringinuse disabled) (dynamic) (Not in use) has taken 7 calls (last was 8732 secs ago)\n', 'Output:          Agent_442 (SIP/374-IPn9TAY) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', 'Output:          Agent_498 (SIP/159-IPnfLhM) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken no calls yet\n', 'Output:          Agent_380 (SIP/373-IPzE0Ma) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', 'Output:          Agent_336 (SIP/339-IP9O9Z2) (ringinuse disabled) (dynamic) (Unavailable) has taken no calls yet\n', 'Output:          Agent_338 (SIP/338-IPi5tbT) (ringinuse disabled) (dynamic) (Unavailable) has taken no calls yet\n', 'Output:          Agent_339 (SIP/336-IPDqFeB) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken no calls yet\n', 'Output:          Agent_479 (SIP/154-IPr39Zr) (ringinuse disabled) (dynamic) (Unavailable) has taken no calls yet\n', 'Output:          Agent_225 (SIP/278-IPezbZg) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', 'Output:          Agent_224 (SIP/277-IPrjQBQ) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', 'Output:          Agent_223 (SIP/276-IPeLQQD) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', 'Output:          Agent_415 (SIP/398-IP62Ton) (ringinuse disabled) (dynamic) (Invalid) has taken no calls yet\n', 'Output:          Agent_411 (SIP/396-IPEiN9R) (ringinuse disabled) (dynamic) (Not in use) has taken 5 calls (last was 10702 secs ago)\n', 'Output:          Agent_422 (SIP/110-IPzfCjJ) (ringinuse disabled) (dynamic) (Unavailable) has taken no calls yet\n', 'Output:          Agent_216 (SIP/268-IPsfacv) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', 'Output:          Agent_213 (SIP/265-IPoxH5b) (ringinuse disabled) (dynamic) (paused) (Not in use) has taken 3 calls (last was 2667 secs ago)\n', 'Output:       Callers: \n', 'Output:          1. SIP/551120872200-000864df (wait: 2:30, prio: 0)\n', 'Output:          2. SIP/5435204040-00086508 (wait: 1:27, prio: 0)\n', 'Output:          3. SIP/551120872200-00086527 (wait: 1:15, prio: 0)\n', 'Output:          4. SIP/551120872200-0008654a (wait: 0:40, prio: 0)\n', 'Output:          5. SIP/551120872200-0008659c (wait: 0:06, prio: 0)\n', 'Output:          6. SIP/551120872200-00086596 (wait: 0:01, prio: 0)\n', 'Output:    \n'], ["Output:    Queue_435 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0% within 0s\n", 'Output:       Members: \n', 'Output:          SIP/388-IPoGO3b (ringinuse disabled) (In use) has taken no calls yet\n', 'Output:          SIP/403-IPuNdIC (ringinuse disabled) (Unavailable) has taken no calls yet\n', 'Output:          SIP/379-IPL8D33 (ringinuse disabled) (In use) has taken no calls yet\n', 'Output:          SIP/287-IPcdhrw (ringinuse disabled) (Unavailable) has taken no calls yet\n', 'Output:          SIP/114-IPgrNRH (ringinuse disabled) (Not in use) has taken no calls yet\n', 'Output:          SIP/359-IPcdAiX (ringinuse disabled) (Not in use) has taken no calls yet\n', 'Output:       No Callers\n', 'Output:    \n'], ["Output:    Queue_500 has 0 calls (max unlimited) in 'ringall' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0% within 0s\n", 'Output:       Members: \n', 'Output:          SIP/105-IPCZncL (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/138-IPtB4BJ (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/374-IPn9TAY (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/125-IPgxdHC (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/157-IPGO4DP (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/213-IPZHgJN (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/338-IPi5tbT (ringinuse disabled) (Unavailable) has taken no calls yet\n', 'Output:          SIP/337-IPtmIFp (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/210-IPu1jOw (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/335-IPvOHVb (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/369-IPlFqAZ (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/399-IPlgNTQ (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/238-IP4Qase (ringinuse disabled) (Unavailable) has taken no calls yet\n', 'Output:          SIP/111-IP4RT8z (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:       No Callers\n', 'Output:    \n'], ["Output:    Queue_501 has 0 calls (max unlimited) in 'ringall' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0% within 0s\n", 'Output:       Members: \n', 'Output:          SIP/263-IP2i5Zq (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/387-IPZ5ZXM (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/283-IPg9X51 (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/271-IP4eb3Q (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/269-IPEGdZ0 (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/392-IPl4lZH (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:       No Callers\n', 'Output:    \n'], ["Output:    Queue_291 has 11 calls (max unlimited) in 'random' strategy (676s holdtime, 880s talktime), W:0, C:29, A:141, SL:0.0% within 0s\n", 'Output:       Members: \n', 'Output:          SIP/105-IPCZncL (ringinuse disabled) (paused) (Not in use) has taken 6 calls (last was 2309 secs ago)\n', 'Output:          SIP/263-IP2i5Zq (ringinuse disabled) (paused) (Unavailable) has taken 5 calls (last was 1735 secs ago)\n', 'Output:          SIP/138-IPtB4BJ (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/387-IPZ5ZXM (ringinuse disabled) (paused) (Not in use) has taken 3 calls (last was 6559 secs ago)\n', 'Output:          Agent_397 (SIP/383-IPc23wN) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/374-IPn9TAY (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/125-IPgxdHC (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/283-IPg9X51 (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/157-IPGO4DP (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/213-IPZHgJN (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/338-IPi5tbT (ringinuse disabled) (Unavailable) has taken no calls yet\n', 'Output:          SIP/337-IPtmIFp (ringinuse disabled) (paused) (Not in use) has taken 3 calls (last was 7342 secs ago)\n', 'Output:          SIP/210-IPu1jOw (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/335-IPvOHVb (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/369-IPlFqAZ (ringinuse disabled) (paused) (Unavailable) has taken 1 calls (last was 14701 secs ago)\n', 'Output:          Agent_375 (SIP/368-IPDZewZ) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/366-IPqqHwa (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:          SIP/399-IPlgNTQ (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/238-IP4Qase (ringinuse disabled) (Unavailable) has taken no calls yet\n', 'Output:          SIP/271-IP4eb3Q (ringinuse disabled) (paused) (Not in use) has taken 1 calls (last was 7955 secs ago)\n', 'Output:          SIP/111-IP4RT8z (ringinuse disabled) (paused) (Not in use) has taken 8 calls (last was 6339 secs ago)\n', 'Output:          SIP/269-IPEGdZ0 (ringinuse disabled) (paused) (Not in use) has taken 2 calls (last was 2844 secs ago)\n', 'Output:          SIP/392-IPl4lZH (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:       Callers: \n', 'Output:          1. SIP/551120872200-00085b93 (wait: 27:45, prio: 0)\n', 'Output:          2. SIP/551120872200-00085cc2 (wait: 24:01, prio: 0)\n', 'Output:          3. SIP/551120872200-00085e58 (wait: 18:11, prio: 0)\n', 'Output:          4. SIP/551120872200-0008605e (wait: 13:25, prio: 0)\n', 'Output:          5. SIP/551120872200-000860c8 (wait: 12:27, prio: 0)\n', 'Output:          6. SIP/551120872200-00086210 (wait: 7:47, prio: 0)\n', 'Output:          7. SIP/551120872200-000862ff (wait: 4:47, prio: 0)\n', 'Output:          8. SIP/551120872200-000862e1 (wait: 4:45, prio: 0)\n', 'Output:          9. SIP/551120872200-000862ed (wait: 4:42, prio: 0)\n', 'Output:          10. SIP/551120872200-00086344 (wait: 3:41, prio: 0)\n', 'Output:          11. SIP/551120872200-0008633a (wait: 3:41, prio: 0)\n', 'Output:    \n'], ["Output:    Queue_238 has 2 calls (max unlimited) in 'ringall' strategy (104s holdtime, 717s talktime), W:0, C:28, A:19, SL:0.0% within 0s\n", 'Output:       Members: \n', 'Output:          SIP/262-IPJM3GO (ringinuse disabled) (paused) (Busy) has taken no calls yet\n', 'Output:          SIP/385-IPTivIr (ringinuse disabled) (paused) (Not in use) has taken 13 calls (last was 2544 secs ago)\n', 'Output:          SIP/315-IPw00cr (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          Agent_304 (SIP/314-IPgfPCZ) (ringinuse disabled) (dynamic) (paused) (Unavailable) has taken no calls yet\n', 'Output:          Agent_240 (SIP/IP-137-VN8Ff) (ringinuse disabled) (dynamic) (paused) (Invalid) has taken no calls yet\n', 'Output:          SIP/IP-176-Jf1ll (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/IP-189-JQQsD (ringinuse disabled) (paused) (Not in use) has taken 1 calls (last was 9920 secs ago)\n', 'Output:          SIP/IP-188-R33In (ringinuse disabled) (paused) (In use) has taken no calls yet\n', 'Output:          SIP/308-IPBA0xb (ringinuse disabled) (paused) (In use) has taken no calls yet\n', 'Output:          SIP/281-IPgV576 (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/280-IP0pOQg (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/279-IPP7Qqg (ringinuse disabled) (paused) (Not in use) has taken 12 calls (last was 995 secs ago)\n', 'Output:          SIP/394-IPDoQmZ (ringinuse disabled) (In use) has taken no calls yet\n', 'Output:          SIP/391-IPcrVn0 (ringinuse disabled) (Not in use) has taken 2 calls (last was 11668 secs ago)\n', 'Output:       Callers: \n', 'Output:          1. SIP/20872200-0008644e (wait: 4:51, prio: 0)\n', 'Output:          2. SIP/20872200-00086572 (wait: 0:55, prio: 0)\n', 'Output:    \n'], ["Output:    Queue_365 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0% within 0s\n", 'Output:       Members: \n', 'Output:          SIP/353-IP2f1fL (ringinuse disabled) (Unavailable) has taken no calls yet\n', 'Output:          SIP/374-IPn9TAY (ringinuse disabled) (paused) (Unavailable) has taken no calls yet\n', 'Output:          SIP/366-IPqqHwa (ringinuse disabled) (paused) (Not in use) has taken no calls yet\n', 'Output:       No Callers\n', 'Output:    \n']]
        queue_parser = QueueParser()
        data = queue_parser._get_list_queue_lines(received_data)
        self.assertEqual(data, expected_data)
        
    def test_get_parser_queue_with_callers(self):
        received_data = '''Queue_1088 has 5 calls (max unlimited) in 'rrmemory' strategy (348s holdtime, 304s talktime), W:10, C:43, A:11, SL:0.0% within 0s
   Members: 
      SIP/IP1489 (ringinuse disabled) (in call) (In use) has taken 3 calls (last was 1912 secs ago)
      SIP/IP1492 (ringinuse disabled) (Unavailable) has taken no calls yet
      SIP/IP1107 (ringinuse disabled) (paused) (Not in use) has taken 4 calls (last was 1386 secs ago)

   Callers: 
      1. IAX2/SERVER_2-13471 (wait: 8:25, prio: 0)
      2. IAX2/SERVER_2-9969 (wait: 0:29, prio: 0)'''
        received_data = received_data.split('\n')
        expect_data = {
            'queuename': 'Queue_1088',
            'total_calls': 5,
            'strategy': 'rrmemory',
            'wait_mean': 348,
            'duration_mean': 304,
            'total_wait_calls': 10,
            'total_completed_calls': 43,
            'total_abandoned_calls': 11,
            'members': [
                {
                    'name': 'SIP/IP1489',
                    'dynamic': None,
                    'in_call': True,
                    'has_paused': False,
                    'paused_time': 0,
                    'reason_paused': None,
                    'logged_time': 0,
                    'total_calls': 3,
                    'last_call_time': 1912,
                    'penalty': 0
                },
                {
                    'name': 'SIP/IP1492',
                    'dynamic': None,
                    'in_call': False,
                    'has_paused': False,
                    'paused_time': 0,
                    'reason_paused': None,
                    'logged_time': 0,
                    'total_calls': 0,
                    'last_call_time': 0,
                    'penalty': 0
                },
                {
                    'name': 'SIP/IP1107',
                    'dynamic': None,
                    'in_call': False,
                    'has_paused': True,
                    'paused_time': 0,
                    'reason_paused': None,
                    'logged_time': 0,
                    'total_calls': 4,
                    'last_call_time': 1386,
                    'penalty': 0
                },
            ],
            'waiting_calls': [
                {
                    'channel': 'IAX2/SERVER_2-13471',
                    'position': 1,
                    'wait_time': 505,
                    'priority': 0
                },
                {
                    'channel': 'IAX2/SERVER_2-9969',
                    'position': 2,
                    'wait_time': 29,
                    'priority': 0
                }
            ]
        }
        parser = QueueParser()
        data = parser._get_parser_queue(received_data)
        self.assertDictEqual(data, expect_data)
    
    def test_get_parser_queue_without_callers(self):
        received_data = '''Queue_1088 has 5 calls (max unlimited) in 'rrmemory' strategy (348s holdtime, 304s talktime), W:10, C:43, A:11, SL:0.0% within 0s
   Members: 
      SIP/IP1489 (ringinuse disabled) (in call) (In use) has taken 3 calls (last was 1912 secs ago)
      SIP/IP1492 (ringinuse disabled) (Unavailable) has taken no calls yet
      SIP/IP1010 (ringinuse disabled) (paused was 4 secs ago) (Not in use) has taken no calls yet (login was 54 secs ago)
   No Callers'''
        received_data = received_data.split('\n')
        expect_data = {
            'queuename': 'Queue_1088',
            'total_calls': 5,
            'strategy': 'rrmemory',
            'wait_mean': 348,
            'duration_mean': 304,
            'total_wait_calls': 10,
            'total_completed_calls': 43,
            'total_abandoned_calls': 11,
            'members': [
                {
                    'name': 'SIP/IP1489',
                    'dynamic': None,
                    'in_call': True,
                    'has_paused': False,
                    'paused_time': 0,
                    'reason_paused': None,
                    'logged_time': 0,
                    'total_calls': 3,
                    'last_call_time': 1912,
                    'penalty': 0
                },
                {
                    'name': 'SIP/IP1492',
                    'dynamic': None,
                    'in_call': False,
                    'has_paused': False,
                    'paused_time': 0,
                    'reason_paused': None,
                    'logged_time': 0,
                    'total_calls': 0,
                    'last_call_time': 0,
                    'penalty': 0
                },
                {
                    'name': 'SIP/IP1010',
                    'dynamic': None,
                    'in_call': False,
                    'has_paused': True,
                    'paused_time': 4,
                    'reason_paused': None,
                    'logged_time': 54,
                    'total_calls': 0,
                    'last_call_time': 0,
                    'penalty': 0
                },
            ],
            'waiting_calls': []
        }
        parser = QueueParser()
        data = parser._get_parser_queue(received_data)
        self.assertDictEqual(data, expect_data)

    def test_get_data_queue(self):
        received_line = "Output: Queue_11 has 3 calls (max unlimited) in 'rrmemory' strategy (10s holdtime, 230s talktime), W:1, C:130, A:5, SL:0.0%, SL2:0.0% within 0s"
        parser = QueueParser()
        data = parser._get_data_queue(received_line)
        expect_data = {
            'queuename': 'Queue_11',
            'total_calls': 3,
            'strategy': 'rrmemory',
            'wait_mean': 10,
            'duration_mean': 230,
            'total_wait_calls': 1,
            'total_completed_calls': 130,
            'total_abandoned_calls': 5
        }
        self.assertDictEqual(data, expect_data)

    def test_get_data_member(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2507382 secs ago) (In use) has taken 1 calls (last was 628 secs ago) (login was 3507382 secs ago)'
        parser = QueueParser()
        data = parser._get_data_member(received_line)
        expect_data = {
            'name': 'SIP/IP-100-CdFaT',
            'dynamic': None,
            'in_call': False,
            'has_paused': True,
            'paused_time': 2507382,
            'reason_paused': None,
            'logged_time': 3507382,
            'total_calls': 1,
            'last_call_time': 628,
            'penalty': 0
        }
        self.assertDictEqual(data, expect_data)
    
    def test_get_data_member_with_penalty(self):
        received_line = 'Output:       SIP/IP-100-CdFaT with penalty 1 (ringinuse disabled) (paused was 2507382 secs ago) (In use) has taken 1 calls (last was 628 secs ago) (login was 3507382 secs ago)'
        parser = QueueParser()
        data = parser._get_data_member(received_line)
        expect_data = {
            'name': 'SIP/IP-100-CdFaT',
            'dynamic': None,
            'in_call': False,
            'has_paused': True,
            'paused_time': 2507382,
            'reason_paused': None,
            'logged_time': 3507382,
            'total_calls': 1,
            'last_call_time': 628,
            'penalty': 1
        }
        self.assertDictEqual(data, expect_data)
    
    def test_get_data_member_dynamic(self):
        received_line = 'Output:       Agent_17 (SIP/IP-101-Q14V2) (ringinuse disabled) (dynamic) (Not in use) has taken no calls yet (login was 4 secs ago)'
        parser = QueueParser()
        data = parser._get_data_member(received_line)
        expect_data = {
            'name': 'SIP/IP-101-Q14V2',
            'dynamic': 'Agent_17',
            'in_call': False,
            'has_paused': False,
            'paused_time': 0,
            'reason_paused': None,
            'logged_time': 4,
            'total_calls': 0,
            'last_call_time': 0,
            'penalty': 0
        }
        self.assertDictEqual(data, expect_data)
    
    def test_get_data_channel(self):
        received_line = 'Output:       1. IAX2/SERVER_2-13471 (wait: 8:25, prio: 0)'
        parser = QueueParser()
        data = parser._get_data_channel(received_line)
        expect_data = {
            'channel': 'IAX2/SERVER_2-13471',
            'position': 1,
            'wait_time': 505,
            'priority': 0
        }
        self.assertDictEqual(data, expect_data)

    def test_get_queuename(self):
        received_line = "Output: Queue_11 has 1 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s"
        parser = QueueParser()
        queuename = parser._get_queuename(received_line)
        self.assertEqual(queuename, 'Queue_11')
    
    def test_get_total_calls(self):
        received_line = "Output: Queue_11 has 1 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s"
        parser = QueueParser()
        quantidade_chamadas_totais = parser._get_total_calls(received_line)
        self.assertEqual(quantidade_chamadas_totais, 1)
    
    def test_get_strategy(self):
        received_line = "Output: Queue_11 has 1 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s"
        parser = QueueParser()
        strategy = parser._get_strategy(received_line)
        self.assertEqual(strategy, 'rrmemory')
    
    def test_get_wait_mean(self):
        received_line = "Output: Queue_11 has 1 calls (max unlimited) in 'rrmemory' strategy (120s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s"
        parser = QueueParser()
        wait_mean = parser._get_wait_mean(received_line)
        self.assertEqual(wait_mean, 120)
    
    def test_get_duration_mean(self):
        received_line = "Output: Queue_11 has 1 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 90s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s"
        parser = QueueParser()
        duration_mean = parser._get_duration_mean(received_line)
        self.assertEqual(duration_mean, 90)

    def test_get_total_wait_calls(self):
        received_line = "Output: Queue_11 has 1 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:2, C:0, A:0, SL:0.0%, SL2:0.0% within 0s"
        parser = QueueParser()
        total_wait_calls = parser._get_total_wait_calls(received_line)
        self.assertEqual(total_wait_calls, 2)
    
    def test_get_total_completed_calls(self):
        received_line = "Output: Queue_11 has 1 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:2, C:5, A:0, SL:0.0%, SL2:0.0% within 0s"
        parser = QueueParser()
        total_completed_calls = parser._get_total_completed_calls(received_line)
        self.assertEqual(total_completed_calls, 5)
    
    def test_get_total_abandoned_calls(self):
        received_line = "Output: Queue_11 has 1 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:2, C:5, A:3, SL:0.0%, SL2:0.0% within 0s"
        parser = QueueParser()
        total_abandoned_calls = parser._get_total_abandoned_calls(received_line)
        self.assertEqual(total_abandoned_calls, 3)
    
    def test_get_queue_member(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2507382 secs ago) (In use) has taken no calls yet (login was 2507382 secs ago)'
        parser = QueueParser()
        queue_member = parser._get_member_name(received_line)
        self.assertEqual(queue_member, 'SIP/IP-100-CdFaT')
    
    def test_get_queue_member_with_penalty(self):
        received_line = 'Output:       SIP/IP-100-CdFaT with penalty 1 (ringinuse disabled) (paused was 2507382 secs ago) (In use) has taken no calls yet (login was 2507382 secs ago)'
        parser = QueueParser()
        queue_member = parser._get_member_name(received_line)
        self.assertEqual(queue_member, 'SIP/IP-100-CdFaT')

    def test_get_member_has_paused(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2507382 secs ago) (In use) has taken no calls yet (login was 2507382 secs ago)'
        parser = QueueParser()
        has_paused = parser._get_member_has_paused(received_line)
        self.assertTrue(has_paused)
    
    def test_get_member_has_paused(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (In use) has taken no calls yet (login was 2507382 secs ago)'
        parser = QueueParser()
        has_paused = parser._get_member_has_paused(received_line)
        self.assertFalse(has_paused)
    
    def test_get_member_paused(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2507382 secs ago) (In use) has taken no calls yet (login was 2507382 secs ago)'
        parser = QueueParser()
        paused_time = parser._get_member_paused(received_line)
        self.assertEqual(paused_time, 2507382)
    
    def test_get_member_not_paused(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (In use) has taken no calls yet (login was 2507382 secs ago)'
        parser = QueueParser()
        paused_time = parser._get_member_paused(received_line)
        self.assertEqual(paused_time, 0)

    def test_get_member_logged(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (In use) has taken no calls yet (login was 2507400 secs ago)'
        parser = QueueParser()
        logged_time = parser._get_member_logged(received_line)
        self.assertEqual(logged_time, 2507400)
    
    def test_get_member_not_logged(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (In use) has taken no calls yet'
        parser = QueueParser()
        logged_time = parser._get_member_logged(received_line)
        self.assertEqual(logged_time, 0)

    def test_get_member_paused_logged(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2507382 secs ago) (In use) has taken no calls yet (login was 2507400 secs ago)'
        parser = QueueParser()
        logged_time = parser._get_member_logged(received_line)
        self.assertEqual(logged_time, 2507400)

    def test_get_member_calls(self):
        received_line = 'Output:       SIP/IP1489 (ringinuse disabled) (In use) has taken 1 calls (last was 628 secs ago)'
        parser = QueueParser()
        total_calls = parser._get_member_calls(received_line)
        self.assertEqual(total_calls, 1)
    
    def test_get_member_no_calls(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (In use) has taken no calls yet (login was 2507400 secs ago)'
        parser = QueueParser()
        total_calls = parser._get_member_calls(received_line)
        self.assertEqual(total_calls, 0)
    
    def test_get_member_last_call(self):
        received_line = 'Output:       SIP/IP1489 (ringinuse disabled) (In use) has taken 1 calls (last was 628 secs ago)'
        parser = QueueParser()
        last_call_time = parser._get_member_last_call(received_line)
        self.assertEqual(last_call_time, 628)
    
    def test_get_member_no_last_call(self):
        received_line = 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (In use) has taken no calls yet (login was 2507400 secs ago)'
        parser = QueueParser()
        total_calls = parser._get_member_last_call(received_line)
        self.assertEqual(total_calls, 0)
    
    def test_get_call_position(self):
        received_line = 'Output:       1. IAX2/SERVER_2-13471 (wait: 8:25, prio: 0)'
        parser = QueueParser()
        total_calls = parser._get_call_position(received_line)
        self.assertEqual(total_calls, 1)

    def test_get_call_channel(self):
        received_line = 'Output:       1. IAX2/SERVER_2-13471 (wait: 8:25, prio: 1)'
        parser = QueueParser()
        call_channel = parser._get_call_channel(received_line)
        self.assertEqual(call_channel, 'IAX2/SERVER_2-13471')
    
    def test_get_call_wait(self):
        received_line = 'Output:       1. IAX2/SERVER_2-13471 (wait: 8:25, prio: 0)'
        parser = QueueParser()
        total_calls = parser._get_call_wait(received_line)
        self.assertEqual(total_calls, 505)
    
    def test_get_call_priority(self):
        received_line = 'Output:       1. IAX2/SERVER_2-13471 (wait: 8:25, prio: 1)'
        parser = QueueParser()
        total_calls = parser._get_call_priority(received_line)
        self.assertEqual(total_calls, 1)

    def test_get_reason_paused(self):
        received_line = 'Output:       SIP/IP-101-Q14V2 (ringinuse disabled) (paused:Reunião was 7 secs ago) (Not in use) has taken no calls yet (login was 2856 secs ago)'
        expected_data = 'Reunião'
        parser = QueueParser()
        reason_paused = parser._get_reason_paused(received_line)
        self.assertEqual(reason_paused, expected_data)
    
    def test_get_reason_paused_not_paused(self):
        received_line = 'Output:       SIP/IP-101-Q14V2 (ringinuse disabled) (Not in use) has taken no calls yet (login was 41 secs ago)'
        expected_data = None
        parser = QueueParser()
        reason_paused = parser._get_reason_paused(received_line)
        self.assertEqual(reason_paused, expected_data)
    
    def test_get_reason_paused_not_reason_paused(self):
        received_line = 'Output:       SIP/IP-101-Q14V2 (ringinuse disabled) (paused was 4 secs ago) (Not in use) has taken no calls yet (login was 54 secs ago)'
        expected_data = None
        parser = QueueParser()
        reason_paused = parser._get_reason_paused(received_line)
        self.assertEqual(reason_paused, expected_data)

    def test_get_penalty(self):
        received_line = 'Output:       SIP/IP-101-Q14V2 with penalty 1 (ringinuse disabled) (paused was 4 secs ago) (Not in use) has taken no calls yet (login was 54 secs ago)'
        expected_data = 1
        parser = QueueParser()
        penalty = parser._get_penalty(received_line)
        self.assertEqual(penalty, expected_data)