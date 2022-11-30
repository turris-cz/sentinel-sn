from sn import SNPipelineBox


def add2(input: int) -> int:
    return input + 2


class TemplateBox(SNPipelineBox):
    def process(self, msg_type, payload):
        if msg_type == "msg/i/should/care/about":
            payload["new_field"] = add2(payload["field"])
            return msg_type, payload
