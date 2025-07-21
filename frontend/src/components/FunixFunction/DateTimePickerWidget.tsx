import { DateTimePicker } from "@mui/x-date-pickers";
import { WidgetProps } from "@rjsf/utils";
import dayjs, { Dayjs } from "dayjs";
import React, { useEffect } from "react";

interface DateTimePickerWidgetProps {
  widget: WidgetProps;
  data: any;
}

const DateTimePickerWidget = (props: DateTimePickerWidgetProps) => {
  const [value, setValue] = React.useState<Dayjs | null>(() => {
    if (props.widget.schema.default) {
      return dayjs(props.widget.schema.default.toString());
    }
    return null;
  });

  const handleChange = (date: Dayjs | null) => {
    if (date) {
      setValue(date);
      props.widget.onChange(date.toISOString());
    } else {
      setValue(null);
      props.widget.onChange(null);
    }
  };

  useEffect(() => {
    if (props.data) {
      setValue(dayjs(props.data.toString()));
    }
  }, [props.data]);

  return (
    <DateTimePicker
      sx={{
        width: "100%",
      }}
      value={value}
      onChange={handleChange}
      format="YYYY-MM-DD HH:mm:ss"
    />
  );
};

export default DateTimePickerWidget;
