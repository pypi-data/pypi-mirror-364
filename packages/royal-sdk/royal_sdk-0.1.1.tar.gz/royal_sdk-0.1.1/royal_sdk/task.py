#https://docs.royalapps.com/r2023/scripting/objects/tasks/royalkeysequencetask.html
class KeySequenceTask:
    def __init__(self, name, key_sequence,no_confirmation_required:bool = False, execution_mode:int = 2):
        self.name = name
        self.key_sequence = key_sequence
        self.no_confirmation_required = no_confirmation_required
        self.execution_mode = execution_mode  # 0 = Do not change, 1 = Keyboard input simulation,2 = Direct mode (where supported)

    def objectify(self) -> dict:
        return {
            "Type": "KeySequenceTask",
            "Name": self.name,
            "KeySequence": self.key_sequence,
            "ExecutionMode": self.execution_mode,
            "NoConfirmationRequired": self.no_confirmation_required
        }

# #https://docs.royalapps.com/r2023/scripting/objects/tasks/royalcommandtask.html
# class CommandTask:
#     def __init__(self, name, command):
#         self.name = name
#         self.command = command

#     def objectify(self) -> dict:
#         return {
#             "Type": "CommandTask",
#             "Name": self.name,
#             "Command": self.command
#         }